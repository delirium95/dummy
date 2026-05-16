from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.post.interfaces import PostRepository
from domain.unit_of_work import UnitOfWork
from domain.user.interfaces import UserRepository
from repositories.post_repository import SAPostRepository
from repositories.user_repository import SAUserRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self._session_maker = session_maker
        self._session: AsyncSession | None = None
        self._committed = False
        self._user_repository: UserRepository | None = None
        self._post_repository: PostRepository | None = None

    @property
    def is_committed(self) -> bool:
        return self._committed

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError(
                'AsyncSession is not initialized. Use "async with uow" before accessing it.'
            )
        return self._session

    @property
    def user_repository(self) -> UserRepository:
        if self._user_repository is None:
            raise RuntimeError('user_repository is not initialized. Use "async with uow" first.')
        return self._user_repository

    @property
    def post_repository(self) -> PostRepository:
        if self._post_repository is None:
            raise RuntimeError('post_repository is not initialized. Use "async with uow" first.')
        return self._post_repository

    async def __aenter__(self) -> Self:
        self._session = self._session_maker()
        self._committed = False
        self._user_repository = SAUserRepository(self._session)
        self._post_repository = SAPostRepository(self._session)
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        try:
            if not self._committed:
                await self.rollback()
        finally:
            if self._session is not None:
                await self._session.close()
            self._session = None
            self._user_repository = None
            self._post_repository = None

    async def commit(self) -> None:
        await self.session.commit()
        self._committed = True

    async def rollback(self) -> None:
        await self.session.rollback()
