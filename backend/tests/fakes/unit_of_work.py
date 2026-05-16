from typing import Self

from domain.post.interfaces import PostRepository
from domain.unit_of_work import UnitOfWork
from domain.user.interfaces import UserRepository
from tests.fakes.post_repository import InMemoryPostRepository
from tests.fakes.user_repository import InMemoryUserRepository


class FakeUnitOfWork(UnitOfWork):
    def __init__(
        self,
        user_repository: InMemoryUserRepository | None = None,
        post_repository: InMemoryPostRepository | None = None,
    ) -> None:
        self._user_repository = user_repository or InMemoryUserRepository()
        self._post_repository = post_repository or InMemoryPostRepository()
        self._committed = False
        self.commit_calls = 0
        self.rollback_calls = 0

    @property
    def is_committed(self) -> bool:
        return self._committed

    @property
    def user_repository(self) -> UserRepository:
        return self._user_repository

    @property
    def post_repository(self) -> PostRepository:
        return self._post_repository

    async def __aenter__(self) -> Self:
        self._committed = False
        return self

    async def commit(self) -> None:
        self._committed = True
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1
