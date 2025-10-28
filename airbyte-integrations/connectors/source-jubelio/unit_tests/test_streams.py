#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests_mock
from source_jubelio.streams import Products, Orders, Contacts, Categories


class TestProducts:
    def test_path(self, config):
        """Test that products stream has correct path"""
        stream = Products(config=config)
        assert stream.path() == "inventory/items/"

    def test_primary_key(self, config):
        """Test that products stream has correct primary key"""
        stream = Products(config=config)
        assert stream.primary_key == "item_group_id"
        
    def test_name(self, config):
        """Test that products stream has correct name"""
        stream = Products(config=config)
        assert stream.name == "products"


class TestOrders:
    def test_path(self, config):
        """Test that orders stream has correct path"""
        stream = Orders(config=config)
        assert stream.path() == "sales/orders/"

    def test_primary_key(self, config):
        """Test that orders stream has correct primary key"""
        stream = Orders(config=config)
        assert stream.primary_key == "salesorder_id"
        
    def test_name(self, config):
        """Test that orders stream has correct name"""
        stream = Orders(config=config)
        assert stream.name == "orders"


class TestContacts:
    def test_path(self, config):
        """Test that contacts stream has correct path"""
        stream = Contacts(config=config)
        assert stream.path() == "contacts/"

    def test_primary_key(self, config):
        """Test that contacts stream has correct primary key"""
        stream = Contacts(config=config)
        assert stream.primary_key == "contact_id"
        
    def test_name(self, config):
        """Test that contacts stream has correct name"""
        stream = Contacts(config=config)
        assert stream.name == "contacts"


class TestCategories:
    def test_path(self, config):
        """Test that categories stream has correct path"""
        stream = Categories(config=config)
        assert stream.path() == "inventory/categories/item-categories/"

    def test_primary_key(self, config):
        """Test that categories stream has correct primary key"""
        stream = Categories(config=config)
        assert stream.primary_key == "category_id"
        
    def test_name(self, config):
        """Test that categories stream has correct name"""
        stream = Categories(config=config)
        assert stream.name == "categories"


class TestStreamAuthentication:
    def test_request_headers(self, config):
        """Test that request headers include authentication"""
        stream = Products(config=config)
        headers = stream.request_headers({})
        
        assert headers["authorization"] == "test_api_key"  # Direct token, not Bearer
        assert headers["Content-Type"] == "application/json"

    def test_url_base(self, config):
        """Test that URL base is set correctly"""
        stream = Products(config=config)
        assert stream.url_base == "https://api2.jubelio.com"