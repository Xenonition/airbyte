#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_jubelio import SourceJubelio


class TestSourceJubelio:
    @patch('source_jubelio.source.requests.get')
    def test_check_connection_success(self, mock_get, config):
        """Test successful connection check"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        source = SourceJubelio()
        status, message = source.check_connection(MagicMock(), config)
        assert status is True
        assert message is None
        
        # Verify the correct API endpoint was called
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "inventory/categories/item-categories" in args[0]
        assert kwargs['headers']['authorization'] == 'test_api_key'

    @patch('source_jubelio.source.requests.get')
    def test_check_connection_auth_failure(self, mock_get, config):
        """Test connection check with authentication failure"""
        # Mock 401 Unauthorized response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        source = SourceJubelio()
        status, message = source.check_connection(MagicMock(), config)
        assert status is False
        assert "Authentication failed" in message

    def test_check_connection_missing_api_key(self, config):
        """Test connection check with missing API key"""
        config_without_key = config.copy()
        del config_without_key["api_key"]
        
        source = SourceJubelio()
        status, message = source.check_connection(MagicMock(), config_without_key)
        assert status is False
        assert "Missing required configuration field: api_key" in message

    def test_check_connection_missing_base_url(self, config):
        """Test connection check with missing base URL"""
        config_without_url = config.copy()
        del config_without_url["base_url"]
        
        source = SourceJubelio()
        status, message = source.check_connection(MagicMock(), config_without_url)
        assert status is False
        assert "Missing required configuration field: base_url" in message

    def test_streams(self, config):
        """Test that streams are returned"""
        source = SourceJubelio()
        streams = source.streams(config)
        assert len(streams) == 2
        stream_names = [stream.name for stream in streams]
        assert "products" in stream_names
        assert "orders" in stream_names