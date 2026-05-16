import httpx
import pytest
import respx

from domain.errors import (
    ExternalSourcePayloadError,
    ExternalSourceTimeoutError,
    ExternalSourceUnavailableError,
)
from infrastructure.dummyjson.client import DummyJSONClient

pytestmark = pytest.mark.unit

BASE_URL = "https://dummyjson.test"


@respx.mock
async def test_fetch_users_parses_paginated_response():
    respx.get(f"{BASE_URL}/users").mock(
        return_value=httpx.Response(
            200,
            json={
                "users": [
                    {
                        "id": 1,
                        "firstName": "Ada",
                        "lastName": "Lovelace",
                        "email": "ada@example.com",
                        "username": "ada",
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            },
        )
    )

    async with httpx.AsyncClient(base_url=BASE_URL) as http_client:
        users = await DummyJSONClient(http_client).fetch_users()

    assert len(users) == 1
    assert users[0].email == "ada@example.com"


@respx.mock
async def test_fetch_users_raises_unavailable_on_5xx():
    respx.get(f"{BASE_URL}/users").mock(return_value=httpx.Response(503))

    async with httpx.AsyncClient(base_url=BASE_URL) as http_client:
        with pytest.raises(ExternalSourceUnavailableError):
            await DummyJSONClient(http_client).fetch_users()


@respx.mock
async def test_fetch_users_raises_timeout():
    respx.get(f"{BASE_URL}/users").mock(side_effect=httpx.ConnectTimeout("timeout"))

    async with httpx.AsyncClient(base_url=BASE_URL) as http_client:
        with pytest.raises(ExternalSourceTimeoutError):
            await DummyJSONClient(http_client).fetch_users()


@respx.mock
async def test_fetch_users_raises_payload_error_on_garbage():
    respx.get(f"{BASE_URL}/users").mock(
        return_value=httpx.Response(200, json={"unexpected": "shape"})
    )

    async with httpx.AsyncClient(base_url=BASE_URL) as http_client:
        with pytest.raises(ExternalSourcePayloadError):
            await DummyJSONClient(http_client).fetch_users()
