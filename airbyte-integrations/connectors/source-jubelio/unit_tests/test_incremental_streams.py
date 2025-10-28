#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from unittest.mock import Mock, patch
from source_jubelio.streams import Orders, Contacts, IncrementalJubelioStream


class TestIncrementalStreams:
    """Test incremental sync functionality for Orders and Contacts streams"""

    @pytest.fixture
    def mock_config(self):
        return {
            "api_key": "test_api_key",
            "base_url": "https://api2.jubelio.com"
        }

    def test_orders_is_incremental(self, mock_config):
        """Test that Orders stream is properly set up for incremental sync"""
        stream = Orders(config=mock_config)
        
        # Check that it inherits from IncrementalMixin
        assert isinstance(stream, IncrementalJubelioStream)
        assert hasattr(stream, 'get_updated_state')
        assert hasattr(stream, 'cursor_field')
        
        # Check cursor field configuration
        assert stream.cursor_field == "last_modified"
        
        # Check incremental parameter name
        assert stream.get_incremental_param_name() == "lastModifiedSince"

    def test_contacts_is_incremental(self, mock_config):
        """Test that Contacts stream is properly set up for incremental sync"""
        stream = Contacts(config=mock_config)
        
        # Check that it inherits from IncrementalMixin
        assert isinstance(stream, IncrementalJubelioStream)
        assert hasattr(stream, 'get_updated_state')
        assert hasattr(stream, 'cursor_field')
        
        # Check cursor field configuration
        assert stream.cursor_field == "last_modified"
        
        # Check incremental parameter name
        assert stream.get_incremental_param_name() == "createdSince"

    def test_get_updated_state_orders(self, mock_config):
        """Test state update logic for Orders stream"""
        stream = Orders(config=mock_config)
        
        # Test initial state (empty)
        current_state = {}
        latest_record = {"last_modified": "2023-12-01T10:00:00Z", "salesorder_id": 123}
        
        updated_state = stream.get_updated_state(current_state, latest_record)
        assert updated_state == {"last_modified": "2023-12-01T10:00:00Z"}
        
        # Test updating with newer record
        current_state = {"last_modified": "2023-12-01T10:00:00Z"}
        latest_record = {"last_modified": "2023-12-01T11:00:00Z", "salesorder_id": 124}
        
        updated_state = stream.get_updated_state(current_state, latest_record)
        assert updated_state == {"last_modified": "2023-12-01T11:00:00Z"}
        
        # Test with older record (should not update)
        current_state = {"last_modified": "2023-12-01T11:00:00Z"}
        latest_record = {"last_modified": "2023-12-01T09:00:00Z", "salesorder_id": 125}
        
        updated_state = stream.get_updated_state(current_state, latest_record)
        assert updated_state == {"last_modified": "2023-12-01T11:00:00Z"}

    def test_get_updated_state_contacts(self, mock_config):
        """Test state update logic for Contacts stream"""
        stream = Contacts(config=mock_config)
        
        # Test initial state (empty)
        current_state = {}
        latest_record = {"last_modified": "2023-12-01T10:00:00Z", "contact_id": 456}
        
        updated_state = stream.get_updated_state(current_state, latest_record)
        assert updated_state == {"last_modified": "2023-12-01T10:00:00Z"}

    def test_request_params_with_state_orders(self, mock_config):
        """Test request parameters include incremental sync parameter for Orders"""
        stream = Orders(config=mock_config)
        
        # Test without state (should not include incremental param)
        params = stream.request_params(stream_state={})
        assert "lastModifiedSince" not in params
        assert params["pageSize"] == 100
        assert params["page"] == 1
        
        # Test with state (should include incremental param)
        stream_state = {"last_modified": "2023-12-01T10:00:00Z"}
        params = stream.request_params(stream_state=stream_state)
        assert params["lastModifiedSince"] == "2023-12-01T10:00:00Z"
        assert params["pageSize"] == 100
        assert params["page"] == 1

    def test_request_params_with_state_contacts(self, mock_config):
        """Test request parameters include incremental sync parameter for Contacts"""
        stream = Contacts(config=mock_config)
        
        # Test without state (should not include incremental param)
        params = stream.request_params(stream_state={})
        assert "createdSince" not in params
        assert params["pageSize"] == 100
        assert params["page"] == 1
        
        # Test with state (should include incremental param)
        stream_state = {"last_modified": "2023-12-01T10:00:00Z"}
        params = stream.request_params(stream_state=stream_state)
        assert params["createdSince"] == "2023-12-01T10:00:00Z"
        assert params["pageSize"] == 100
        assert params["page"] == 1

    def test_request_params_with_pagination_and_state(self, mock_config):
        """Test that incremental params work with pagination"""
        stream = Orders(config=mock_config)
        
        stream_state = {"last_modified": "2023-12-01T10:00:00Z"}
        next_page_token = {"page": 2}
        
        params = stream.request_params(
            stream_state=stream_state,
            next_page_token=next_page_token
        )
        
        # Should include both incremental and pagination parameters
        assert params["lastModifiedSince"] == "2023-12-01T10:00:00Z"
        assert params["page"] == 2
        assert params["pageSize"] == 100

    def test_state_with_missing_cursor_field(self, mock_config):
        """Test handling of records that don't have the cursor field"""
        stream = Orders(config=mock_config)
        
        current_state = {"last_modified": "2023-12-01T10:00:00Z"}
        record_without_cursor = {"salesorder_id": 123}  # Missing last_modified
        
        # Should not update state if cursor field is missing
        updated_state = stream.get_updated_state(current_state, record_without_cursor)
        assert updated_state == current_state