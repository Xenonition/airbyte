#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class JubelioStream(HttpStream):
    """
    Base stream class for Jubelio API streams
    """

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.base_url = config.get("base_url", "https://api2.jubelio.com")
        self.api_key = config.get("api_key")

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
        TODO: Implement based on Jubelio API pagination format
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Return request parameters
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse the response and yield records
        TODO: Implement based on Jubelio API response format
        """
        response_json = response.json()
        
        # TODO: Modify this based on actual Jubelio API response structure
        if isinstance(response_json, list):
            yield from response_json
        elif isinstance(response_json, dict) and "data" in response_json:
            yield from response_json["data"]
        else:
            yield response_json


class Products(JubelioStream):
    """
    Stream for Jubelio products
    """
    
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Return the API endpoint path for products
        TODO: Update with actual Jubelio API endpoint
        """
        return "products"


class Orders(JubelioStream):
    """
    Stream for Jubelio orders
    """
    
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Return the API endpoint path for orders
        TODO: Update with actual Jubelio API endpoint
        """
        return "orders"