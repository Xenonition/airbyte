#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests_mock
from source_jubelio.streams import JubelioStream, Products, Orders


class TestJubelioStream:
    def test_request_headers(self, config):
        """Test that request headers include authentication"""
        stream = JubelioStream(config=config)
        headers = stream.request_headers({})
        
        assert headers["Authorization"] == "Bearer test_api_key"
        assert headers["Content-Type"] == "application/json"

    def test_url_base(self, config):
        """Test that URL base is set correctly"""
        stream = JubelioStream(config=config)
        assert stream.url_base == "https://api.jubelio.com"


class TestProducts:
    def test_path(self, config):
        """Test that products stream has correct path"""
        stream = Products(config=config)
        assert stream.path() == "products"

    def test_primary_key(self, config):
        """Test that products stream has correct primary key"""
        stream = Products(config=config)
        assert stream.primary_key == "id"


class TestOrders:
    def test_path(self, config):
        """Test that orders stream has correct path"""
        stream = Orders(config=config)
        assert stream.path() == "orders"

    def test_primary_key(self, config):
        """Test that orders stream has correct primary key"""
        stream = Orders(config=config)
        assert stream.primary_key == "id"