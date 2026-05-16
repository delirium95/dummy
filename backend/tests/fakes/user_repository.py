from datetime import datetime

from domain.error_messages import EMAIL_ALREADY_EXISTS, USER_NOT_FOUND, USERNAME_ALREADY_EXISTS
from domain.errors import (
    EmailAlreadyExistsError,
    NotFoundUserError,
    UsernameAlreadyExistsError,
    ValidationError,
)
from domain.ids import ExternalUserID, UserID
from domain.shared.pagination import Page, PageRequest, SortDirection
from domain.user.interfaces import UserRepository
from domain.user.model import NewUserData, UserModel
from domain.user.value_objects import Email, Username


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, UserModel] = {}
        self._next_id = 1

    async def add(self, obj: UserModel, /) -> UserModel:
        self._check_unique(
            email=obj.email.value, username=obj.username.value, exclude_id=int(obj.id)
        )
        self._users[int(obj.id)] = obj
        self._next_id = max(self._next_id, int(obj.id) + 1)
        return obj

    async def create(self, data: NewUserData, /, *, now: datetime) -> UserModel:
        self._check_unique(email=data.email.value, username=data.username.value, exclude_id=None)
        user_id = UserID(self._next_id)
        self._next_id += 1
        user = UserModel(
            id=user_id,
            external_id=data.external_id,
            name=data.name,
            email=data.email,
            username=data.username,
            created_at=now,
            updated_at=now,
        )
        self._users[int(user_id)] = user
        return user

    async def update(self, obj: UserModel, /) -> UserModel:
        if int(obj.id) not in self._users:
            raise NotFoundUserError(USER_NOT_FOUND)
        self._check_unique(
            email=obj.email.value, username=obj.username.value, exclude_id=int(obj.id)
        )
        self._users[int(obj.id)] = obj
        return obj

    async def get(
        self,
        id_: UserID | None = None,
        /,
        *,
        external_id: ExternalUserID | None = None,
        email: Email | None = None,
        username: Username | None = None,
    ) -> UserModel | None:
        for user in self._users.values():
            if id_ is not None and int(user.id) != int(id_):
                continue
            if external_id is not None and (
                user.external_id is None or int(user.external_id) != int(external_id)
            ):
                continue
            if email is not None and user.email.value != email.value:
                continue
            if username is not None and user.username.value != username.value:
                continue
            return user
        return None

    async def delete(self, id_: UserID, /) -> None:
        if int(id_) not in self._users:
            raise NotFoundUserError(USER_NOT_FOUND)
        del self._users[int(id_)]

    async def list_(self, *, page: PageRequest) -> Page[UserModel]:
        if page.sort.field not in self.SORTABLE_FIELDS:
            raise ValidationError(f"unsortable field: {page.sort.field}")

        items = list(self._users.values())
        items.sort(
            key=self._sort_key(page.sort.field), reverse=page.sort.direction == SortDirection.DESC
        )
        sliced = items[page.offset : page.offset + page.limit]
        return Page[UserModel](items=sliced, total=len(items), limit=page.limit, offset=page.offset)

    async def upsert_by_external_id(
        self, data: NewUserData, /, *, now: datetime
    ) -> tuple[UserModel, bool]:
        if data.external_id is None:
            raise ValidationError("upsert_by_external_id requires external_id")
        existing = await self.get(external_id=data.external_id)
        if existing is None:
            user_id = UserID(self._next_id)
            self._next_id += 1
            user = UserModel(
                id=user_id,
                external_id=data.external_id,
                name=data.name,
                email=data.email,
                username=data.username,
                created_at=now,
                updated_at=now,
            )
            self._users[int(user_id)] = user
            return user, True
        updated = existing.model_copy(
            update={
                "name": data.name,
                "email": data.email,
                "username": data.username,
                "updated_at": now,
            }
        )
        self._users[int(existing.id)] = updated
        return updated, False

    def _check_unique(self, *, email: str, username: str, exclude_id: int | None) -> None:
        for user in self._users.values():
            if exclude_id is not None and int(user.id) == exclude_id:
                continue
            if user.email.value == email:
                raise EmailAlreadyExistsError(EMAIL_ALREADY_EXISTS)
            if user.username.value == username:
                raise UsernameAlreadyExistsError(USERNAME_ALREADY_EXISTS)

    @staticmethod
    def _sort_key(field: str):
        def key(u: UserModel):
            match field:
                case "id":
                    return int(u.id)
                case "first_name":
                    return u.name.first
                case "last_name":
                    return u.name.last
                case "email":
                    return u.email.value
                case "username":
                    return u.username.value
                case "created_at":
                    return u.created_at
                case _:
                    return int(u.id)

        return key
