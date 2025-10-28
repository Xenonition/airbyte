#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(name="config")
def config_fixture():
    """
    Sample configuration for testing
    """
    return {
        "api_key": "test_api_key",
        "base_url": "https://api2.jubelio.com",
        "start_date": "2021-01-01T00:00:00Z"
    }