import httpx
from pydantic import ValidationError as PydanticValidationError

from domain.error_messages import (
    EXTERNAL_SOURCE_PAYLOAD,
    EXTERNAL_SOURCE_TIMEOUT,
    EXTERNAL_SOURCE_UNAVAILABLE,
)
from domain.errors import (
    ExternalSourcePayloadError,
    ExternalSourceTimeoutError,
    ExternalSourceUnavailableError,
)
from domain.sync.dto import RemotePost, RemoteUser
from domain.sync.interfaces import ExternalPostSource, ExternalUserSource
from infrastructure.dummyjson.payload import (
    PostsListPayload,
    UsersListPayload,
)

_PAGE_SIZE = 100


class DummyJSONClient(ExternalUserSource, ExternalPostSource):
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def fetch_users(self) -> list[RemoteUser]:
        result: list[RemoteUser] = []
        for raw in await self._fetch_all("/users", "users"):
            payload = self._parse_users_page(raw)
            for u in payload.users:
                result.append(
                    RemoteUser(
                        external_id=u.id,
                        first_name=u.first_name,
                        last_name=u.last_name,
                        email=u.email,
                        username=u.username,
                    )
                )
        return result

    async def fetch_posts(self) -> list[RemotePost]:
        result: list[RemotePost] = []
        for raw in await self._fetch_all("/posts", "posts"):
            payload = self._parse_posts_page(raw)
            for p in payload.posts:
                result.append(
                    RemotePost(
                        external_id=p.id,
                        user_external_id=p.user_id,
                        title=p.title,
                        body=p.body,
                        tags=tuple(p.tags),
                        reactions_likes=p.reactions.likes,
                        reactions_dislikes=p.reactions.dislikes,
                        views=p.views,
                    )
                )
        return result

    async def _fetch_all(self, path: str, items_key: str) -> list[dict]:
        pages: list[dict] = []
        skip = 0
        while True:
            data = await self._get(path, params={"limit": _PAGE_SIZE, "skip": skip})
            pages.append(data)
            total = int(data.get("total", 0))
            received = len(data.get(items_key, []) or [])
            skip += received
            if received == 0 or skip >= total:
                break
        return pages

    async def _get(self, path: str, *, params: dict) -> dict:
        try:
            response = await self._http_client.get(path, params=params)
        except httpx.TimeoutException as e:
            raise ExternalSourceTimeoutError(EXTERNAL_SOURCE_TIMEOUT) from e
        except httpx.HTTPError as e:
            raise ExternalSourceUnavailableError(EXTERNAL_SOURCE_UNAVAILABLE) from e

        if response.status_code >= 400:
            raise ExternalSourceUnavailableError(
                f"{EXTERNAL_SOURCE_UNAVAILABLE} status={response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as e:
            raise ExternalSourcePayloadError(EXTERNAL_SOURCE_PAYLOAD) from e

        if not isinstance(data, dict):
            raise ExternalSourcePayloadError(EXTERNAL_SOURCE_PAYLOAD)
        return data

    @staticmethod
    def _parse_users_page(raw: dict) -> UsersListPayload:
        try:
            return UsersListPayload.model_validate(raw)
        except PydanticValidationError as e:
            raise ExternalSourcePayloadError(EXTERNAL_SOURCE_PAYLOAD) from e

    @staticmethod
    def _parse_posts_page(raw: dict) -> PostsListPayload:
        try:
            return PostsListPayload.model_validate(raw)
        except PydanticValidationError as e:
            raise ExternalSourcePayloadError(EXTERNAL_SOURCE_PAYLOAD) from e
