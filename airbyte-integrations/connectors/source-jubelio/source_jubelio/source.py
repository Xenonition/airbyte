#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple
import logging

import requests
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import JubelioStream, Products, Orders, Contacts, Categories


class SourceJubelio(AbstractSource):
    """
    Source implementation for Jubelio API.
    """

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Check if the provided configuration can be used to connect to the underlying API

        Args:
            logger: Logger instance
            config: User input configuration to connect to the underlying API

        Returns:
            A tuple of (connection_successful, error_message_if_failed)
        """
        try:
            # Validate required configuration fields are present
            required_fields = ["api_key", "base_url"]
            
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required configuration field: {field}"
            
            # Test actual API connection using a lightweight endpoint
            base_url = config.get("base_url", "https://api2.jubelio.com")
            api_key = config.get("api_key")
            
            # Remove trailing slash if present
            base_url = base_url.rstrip("/")
            
            # Use the inventory categories endpoint as it's lightweight for connection testing
            test_url = f"{base_url}/inventory/categories/item-categories/"
            
            headers = {
                "authorization": api_key,  # Based on OpenAPI spec - direct token, not Bearer
                "Content-Type": "application/json",
            }
            
            logger.info(f"Testing connection to Jubelio API at {test_url}")
            
            # Make test request with timeout
            response = requests.get(test_url, headers=headers, timeout=30)
            
            # Check for authentication errors
            if response.status_code == 401:
                return False, "Authentication failed. Please check your API key."
            
            # Check for authorization errors
            if response.status_code == 403:
                return False, "Access forbidden. Please check your API key permissions."
            
            # Check for not found - might indicate wrong base URL
            if response.status_code == 404:
                return False, f"API endpoint not found. Please verify the base_url: {base_url}"
            
            # Check for server errors
            if response.status_code >= 500:
                return False, f"Server error from Jubelio API: {response.status_code}"
            
            # Check for other client errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"API error: {response.status_code}")
                except:
                    error_message = f"API error: {response.status_code} - {response.text[:200]}"
                return False, error_message
            
            # Success - connection is working
            if response.status_code == 200:
                logger.info("Successfully connected to Jubelio API")
                return True, None
            
            # Unexpected status code
            return False, f"Unexpected response from API: {response.status_code}"
            
        except requests.exceptions.Timeout:
            return False, "Connection timeout. Please check your network connection and base_url."
        except requests.exceptions.ConnectionError:
            return False, "Failed to connect to Jubelio API. Please check your base_url and network connection."
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during connection check: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Return a list of streams for this source

        Args:
            config: User input configuration to connect to the underlying API

        Returns:
            List of streams
        """
        return [
            Products(config=config),
            Orders(config=config),
            Contacts(config=config),
            Categories(config=config),
        ]