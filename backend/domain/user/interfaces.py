from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from domain.common.repository import AbstractRepository
from domain.ids import ExternalUserID, UserID
from domain.shared.pagination import Page, PageRequest
from domain.user.model import NewUserData, UserModel
from domain.user.value_objects import Email, FullName, Username


class UserRepository(AbstractRepository[UserID, UserModel]):
    SORTABLE_FIELDS: frozenset[str] = frozenset(
        {"id", "first_name", "last_name", "email", "username", "created_at"}
    )

    @abstractmethod
    async def add(self, obj: UserModel, /) -> UserModel: ...

    @abstractmethod
    async def create(self, data: NewUserData, /, *, now: datetime) -> UserModel:
        """Insert a new user, letting the database assign the id.

        Raises:
            EmailAlreadyExistsError: if email is already in use.
            UsernameAlreadyExistsError: if username is already in use.
        """

    @abstractmethod
    async def update(self, obj: UserModel, /) -> UserModel: ...

    @abstractmethod
    async def get(
        self,
        id_: UserID | None = None,
        /,
        *,
        external_id: ExternalUserID | None = None,
        email: Email | None = None,
        username: Username | None = None,
    ) -> UserModel | None: ...

    @abstractmethod
    async def delete(self, id_: UserID, /) -> None: ...

    @abstractmethod
    async def list_(self, *, page: PageRequest) -> Page[UserModel]: ...

    @abstractmethod
    async def upsert_by_external_id(
        self, data: NewUserData, /, *, now: datetime
    ) -> tuple[UserModel, bool]:
        """Upsert by external id. Returns (user, was_created)."""


class ListUsersUseCase(Protocol):
    async def __call__(self, page: PageRequest) -> Page[UserModel]: ...


class GetUserUseCase(Protocol):
    async def __call__(self, user_id: UserID) -> UserModel: ...


class CreateUserUseCase(Protocol):
    async def __call__(self, data: NewUserData) -> UserModel: ...


class UpdateUserUseCase(Protocol):
    async def __call__(
        self,
        user_id: UserID,
        *,
        name: FullName | None = None,
        email: Email | None = None,
        username: Username | None = None,
    ) -> UserModel: ...


class DeleteUserUseCase(Protocol):
    async def __call__(self, user_id: UserID) -> None: ...
