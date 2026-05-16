from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.error_messages import (
    EMAIL_ALREADY_EXISTS,
    USER_NOT_FOUND,
    USERNAME_ALREADY_EXISTS,
)
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
from infrastructure.database.models import UserRow
from repositories._mappers import user_row_to_model

_SORT_COLUMNS = {
    "id": UserRow.id,
    "first_name": UserRow.first_name,
    "last_name": UserRow.last_name,
    "email": UserRow.email,
    "username": UserRow.username,
    "created_at": UserRow.created_at,
}


class SAUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: UserModel, /) -> UserModel:
        row = self._to_row(obj)
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            self._translate_unique_violation(e)
            raise
        await self.session.refresh(row)
        return user_row_to_model(row)

    async def create(self, data: NewUserData, /, *, now: datetime) -> UserModel:
        row = UserRow(
            external_id=int(data.external_id) if data.external_id is not None else None,
            first_name=data.name.first,
            last_name=data.name.last,
            email=data.email.value,
            username=data.username.value,
            created_at=now,
            updated_at=now,
        )
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            self._translate_unique_violation(e)
            raise
        await self.session.refresh(row)
        return user_row_to_model(row)

    async def update(self, obj: UserModel, /) -> UserModel:
        row = await self.session.get(UserRow, int(obj.id))
        if row is None:
            raise NotFoundUserError(USER_NOT_FOUND)
        row.external_id = int(obj.external_id) if obj.external_id is not None else None
        row.first_name = obj.name.first
        row.last_name = obj.name.last
        row.email = obj.email.value
        row.username = obj.username.value
        row.updated_at = obj.updated_at
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            self._translate_unique_violation(e)
            raise
        return user_row_to_model(row)

    async def get(
        self,
        id_: UserID | None = None,
        /,
        *,
        external_id: ExternalUserID | None = None,
        email: Email | None = None,
        username: Username | None = None,
    ) -> UserModel | None:
        stmt = select(UserRow)
        if id_ is not None:
            stmt = stmt.where(UserRow.id == int(id_))
        if external_id is not None:
            stmt = stmt.where(UserRow.external_id == int(external_id))
        if email is not None:
            stmt = stmt.where(UserRow.email == email.value)
        if username is not None:
            stmt = stmt.where(UserRow.username == username.value)
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return None
        return user_row_to_model(row)

    async def delete(self, id_: UserID, /) -> None:
        row = await self.session.get(UserRow, int(id_))
        if row is None:
            raise NotFoundUserError(USER_NOT_FOUND)
        await self.session.delete(row)
        await self.session.flush()

    async def list_(self, *, page: PageRequest) -> Page[UserModel]:
        if page.sort.field not in self.SORTABLE_FIELDS:
            raise ValidationError(f"unsortable field: {page.sort.field}")

        column = _SORT_COLUMNS[page.sort.field]
        order = column.asc() if page.sort.direction == SortDirection.ASC else column.desc()

        total = (await self.session.execute(select(func.count()).select_from(UserRow))).scalar_one()
        stmt = (
            select(UserRow).order_by(order, UserRow.id.asc()).limit(page.limit).offset(page.offset)
        )
        rows = (await self.session.execute(stmt)).scalars().all()

        return Page[UserModel](
            items=[user_row_to_model(r) for r in rows],
            total=int(total),
            limit=page.limit,
            offset=page.offset,
        )

    async def upsert_by_external_id(
        self, data: NewUserData, /, *, now: datetime
    ) -> tuple[UserModel, bool]:
        if data.external_id is None:
            raise ValidationError("upsert_by_external_id requires external_id")

        existing = (
            await self.session.execute(
                select(UserRow).where(UserRow.external_id == int(data.external_id))
            )
        ).scalar_one_or_none()

        if existing is None:
            row = UserRow(
                external_id=int(data.external_id),
                first_name=data.name.first,
                last_name=data.name.last,
                email=data.email.value,
                username=data.username.value,
                created_at=now,
                updated_at=now,
            )
            self.session.add(row)
            await self.session.flush()
            await self.session.refresh(row)
            return user_row_to_model(row), True

        changed = (
            existing.first_name != data.name.first
            or existing.last_name != data.name.last
            or existing.email != data.email.value
            or existing.username != data.username.value
        )
        if changed:
            existing.first_name = data.name.first
            existing.last_name = data.name.last
            existing.email = data.email.value
            existing.username = data.username.value
            existing.updated_at = now
            await self.session.flush()
        return user_row_to_model(existing), False

    @staticmethod
    def _to_row(obj: UserModel) -> UserRow:
        return UserRow(
            id=int(obj.id),
            external_id=int(obj.external_id) if obj.external_id is not None else None,
            first_name=obj.name.first,
            last_name=obj.name.last,
            email=obj.email.value,
            username=obj.username.value,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _translate_unique_violation(e: IntegrityError) -> None:
        message = str(e.orig).lower() if e.orig is not None else str(e).lower()
        if "uq_users_email" in message or "users_email" in message:
            raise EmailAlreadyExistsError(EMAIL_ALREADY_EXISTS) from e
        if "uq_users_username" in message or "users_username" in message:
            raise UsernameAlreadyExistsError(USERNAME_ALREADY_EXISTS) from e
