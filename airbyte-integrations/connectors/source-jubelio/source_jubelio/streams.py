#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, MutableMapping
from datetime import datetime

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import IncrementalMixin


class JubelioStream(HttpStream):
    """
    Base stream class for Jubelio API streams
    """

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.base_url = config.get("base_url", "https://api2.jubelio.com")
        self.api_key = config.get("api_key")
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def url_base(self) -> str:
        """
        Returns the base URL for the API
        """
        return self.base_url

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return the JSON schema for this stream
        """
        schema_file_path = Path(__file__).parent / "schemas" / f"{self.name}.json"
        if schema_file_path.exists():
            with open(schema_file_path, "r") as f:
                return json.load(f)
        else:
            # Fallback to basic schema if specific schema file doesn't exist
            return {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "type": "object",
                "additionalProperties": True
            }

    @property
    def url_base(self) -> str:
        """
        Returns the base URL for the API
        """
        return self.base_url

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Return headers for API requests
        """
        return {
            "authorization": self.api_key,  # Direct token based on OpenAPI spec
            "Content-Type": "application/json",
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Return next page token if pagination is supported
        Jubelio API uses page-based pagination with page and pageSize parameters
        """
        try:
            response_json = response.json()
            
            # Check if this is a paginated response with data and totalCount
            if isinstance(response_json, dict) and "data" in response_json and "totalCount" in response_json:
                current_params = response.request.url.split('?')[1] if '?' in response.request.url else ""
                params = dict(param.split('=') for param in current_params.split('&') if '=' in param)
                
                current_page = int(params.get('page', 1))
                page_size = int(params.get('pageSize', 25))
                total_count = response_json.get("totalCount", 0)
                
                # Calculate if there are more pages
                if (current_page * page_size) < total_count:
                    return {"page": current_page + 1}
                    
        except (ValueError, KeyError, AttributeError) as e:
            self._logger.warning(f"Error parsing pagination from response: {e}")
            
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Return request parameters with pagination support
        """
        params = {
            "pageSize": 100,  # Reasonable page size for API calls
            "page": 1,
        }
        
        # Add pagination if next_page_token is provided
        if next_page_token:
            params.update(next_page_token)
            
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse the response and yield records
        Jubelio API typically returns data in a structured format with a 'data' field
        """
        try:
            response_json = response.json()
            
            # Handle different response structures
            if isinstance(response_json, dict):
                # Most Jubelio endpoints return data in a 'data' field
                if "data" in response_json:
                    data = response_json["data"]
                    if isinstance(data, list):
                        yield from data
                    else:
                        yield data
                else:
                    # Some endpoints might return data directly
                    yield response_json
            elif isinstance(response_json, list):
                # Direct list response
                yield from response_json
            else:
                self._logger.warning(f"Unexpected response format: {type(response_json)}")
                
        except ValueError as e:
            self._logger.error(f"Failed to parse JSON response: {e}")
            # Yield empty to prevent breaking the sync
            return


class IncrementalJubelioStream(JubelioStream, IncrementalMixin):
    """
    Base class for incremental Jubelio streams that support state and checkpointing
    """
    
    # Cursor field for tracking incremental state - should be overridden in subclasses
    cursor_field: str = "last_modified"
    
    def get_updated_state(self, current_stream_state: Mapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine how to update the stream state given the latest record.
        """
        current_cursor_value = current_stream_state.get(self.cursor_field, "")
        latest_cursor_value = latest_record.get(self.cursor_field, "")
        
        # Use the latest cursor value if it's greater than current
        if latest_cursor_value > current_cursor_value:
            return {self.cursor_field: latest_cursor_value}
        return current_stream_state

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Optional[Mapping[str, Any]] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> MutableMapping[str, Any]:
        """
        Add incremental sync parameters to the request
        """
        # Convert the base params to a mutable mapping
        base_params = super().request_params(stream_state, stream_slice or {}, next_page_token or {})
        if isinstance(base_params, dict):
            params = base_params
        else:
            params = dict(base_params)
        
        # Add the cursor value to the request if we have state
        cursor_value = stream_state.get(self.cursor_field)
        if cursor_value:
            # Different endpoints use different parameter names for temporal filtering
            date_param = self.get_incremental_param_name()
            if date_param:
                params[date_param] = cursor_value
                
        return params
    
    def get_incremental_param_name(self) -> Optional[str]:
        """
        Override in subclasses to specify the API parameter name for incremental sync
        Returns None if the endpoint doesn't support incremental sync via API params
        """
        return None


class Products(JubelioStream):
    """
    Stream for Jubelio products/inventory items
    Based on the /inventory/items/ endpoint
    """
    
    primary_key = "item_group_id"
    name = "products"

    def path(
        self, stream_state: Optional[Mapping[str, Any]] = None, stream_slice: Optional[Mapping[str, Any]] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        Return the API endpoint path for products
        """
        return "inventory/items/"


class Orders(IncrementalJubelioStream):
    """
    Stream for Jubelio sales orders with incremental sync support
    Based on the /sales/orders/ endpoint
    Supports incremental sync via lastModifiedSince parameter
    """
    
    primary_key = "salesorder_id"
    name = "orders"
    cursor_field = "last_modified"

    def path(
        self, stream_state: Optional[Mapping[str, Any]] = None, stream_slice: Optional[Mapping[str, Any]] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        Return the API endpoint path for orders
        """
        return "sales/orders/"
    
    def get_incremental_param_name(self) -> Optional[str]:
        """
        Orders endpoint supports lastModifiedSince parameter for incremental sync
        """
        return "lastModifiedSince"


class Contacts(IncrementalJubelioStream):
    """
    Stream for Jubelio contacts (customers and suppliers) with incremental sync support
    Based on the /contacts/ endpoint
    Supports incremental sync via createdSince parameter
    """
    
    primary_key = "contact_id"
    name = "contacts"
    cursor_field = "last_modified"

    def path(
        self, stream_state: Optional[Mapping[str, Any]] = None, stream_slice: Optional[Mapping[str, Any]] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        Return the API endpoint path for contacts
        """
        return "contacts/"
    
    def get_incremental_param_name(self) -> Optional[str]:
        """
        Contacts endpoint supports createdSince parameter for incremental sync
        """
        return "createdSince"


class Categories(JubelioStream):
    """
    Stream for Jubelio item categories
    Based on the /inventory/categories/item-categories/ endpoint
    """
    
    primary_key = "category_id"
    name = "categories"

    def path(
        self, stream_state: Optional[Mapping[str, Any]] = None, stream_slice: Optional[Mapping[str, Any]] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        Return the API endpoint path for categories
        """
        return "inventory/categories/item-categories/"