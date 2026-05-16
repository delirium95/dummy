from domain.error_messages import USER_NOT_FOUND
from domain.errors import NotFoundUserError
from domain.ids import UserID
from domain.shared.clock import Clock
from domain.shared.pagination import Page, PageRequest
from domain.unit_of_work import UnitOfWork
from domain.user.interfaces import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from domain.user.model import NewUserData, UserModel
from domain.user.value_objects import Email, FullName, Username


class ListUsersUseCaseImpl(ListUsersUseCase):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def __call__(self, page: PageRequest) -> Page[UserModel]:
        async with self.uow as uow:
            return await uow.user_repository.list_(page=page)


class GetUserUseCaseImpl(GetUserUseCase):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def __call__(self, user_id: UserID) -> UserModel:
        async with self.uow as uow:
            user = await uow.user_repository.get(user_id)
            if user is None:
                raise NotFoundUserError(USER_NOT_FOUND)
            return user


class CreateUserUseCaseImpl(CreateUserUseCase):
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self.uow = uow
        self.clock = clock

    async def __call__(self, data: NewUserData) -> UserModel:
        async with self.uow as uow:
            created = await uow.user_repository.create(data, now=self.clock.now())
            await uow.commit()
            return created


class UpdateUserUseCaseImpl(UpdateUserUseCase):
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self.uow = uow
        self.clock = clock

    async def __call__(
        self,
        user_id: UserID,
        *,
        name: FullName | None = None,
        email: Email | None = None,
        username: Username | None = None,
    ) -> UserModel:
        now = self.clock.now()
        async with self.uow as uow:
            current = await uow.user_repository.get(user_id)
            if current is None:
                raise NotFoundUserError(USER_NOT_FOUND)
            updated = current
            if name is not None:
                updated = updated.rename(name=name, now=now)
            if email is not None:
                updated = updated.change_email(email=email, now=now)
            if username is not None:
                updated = updated.change_username(username=username, now=now)
            if updated is current:
                return current
            persisted = await uow.user_repository.update(updated)
            await uow.commit()
            return persisted


class DeleteUserUseCaseImpl(DeleteUserUseCase):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def __call__(self, user_id: UserID) -> None:
        async with self.uow as uow:
            await uow.user_repository.delete(user_id)
            await uow.commit()
