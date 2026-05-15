from abc import ABC, abstractmethod
from typing import Protocol

from domain.sync.dto import RemotePost, RemoteUser, SyncResult


class ExternalUserSource(ABC):
    @abstractmethod
    async def fetch_users(self) -> list[RemoteUser]:
        """Fetch all users from the upstream source.

        Raises:
            ExternalSourceTimeoutError: on connect/read timeout.
            ExternalSourceUnavailableError: on non-2xx response.
            ExternalSourcePayloadError: when payload cannot be parsed.
        """


class ExternalPostSource(ABC):
    @abstractmethod
    async def fetch_posts(self) -> list[RemotePost]:
        """Fetch all posts from the upstream source. See ExternalUserSource for raises."""


class SyncDataUseCase(Protocol):
    async def __call__(self) -> SyncResult: ...
