from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.error_messages import POST_AUTHOR_NOT_FOUND, POST_NOT_FOUND
from domain.errors import (
    NotFoundPostError,
    PostAuthorNotFoundError,
    ValidationError,
)
from domain.ids import ExternalPostID, PostID, UserID
from domain.post.interfaces import PostRepository
from domain.post.model import NewPostData, PostModel
from domain.shared.pagination import Page, PageRequest, SortDirection
from infrastructure.database.models import PostRow
from repositories._mappers import post_row_to_model

_SORT_COLUMNS = {
    "id": PostRow.id,
    "title": PostRow.title,
    "user_id": PostRow.user_id,
    "views": PostRow.views,
    "reactions_likes": PostRow.reactions_likes,
    "created_at": PostRow.created_at,
}


class SAPostRepository(PostRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: PostModel, /) -> PostModel:
        row = PostRow(
            id=int(obj.id),
            external_id=int(obj.external_id) if obj.external_id is not None else None,
            user_id=int(obj.user_id),
            title=obj.title.value,
            body=obj.body.value,
            tags=list(obj.tags.values),
            reactions_likes=obj.reactions_likes,
            reactions_dislikes=obj.reactions_dislikes,
            views=obj.views,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            self._translate_fk_violation(e)
            raise
        await self.session.refresh(row)
        return post_row_to_model(row)

    async def create(self, data: NewPostData, /, *, now: datetime) -> PostModel:
        row = PostRow(
            external_id=int(data.external_id) if data.external_id is not None else None,
            user_id=int(data.user_id),
            title=data.title.value,
            body=data.body.value,
            tags=list(data.tags.values),
            reactions_likes=data.reactions_likes,
            reactions_dislikes=data.reactions_dislikes,
            views=data.views,
            created_at=now,
            updated_at=now,
        )
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            self._translate_fk_violation(e)
            raise
        await self.session.refresh(row)
        return post_row_to_model(row)

    async def update(self, obj: PostModel, /) -> PostModel:
        row = await self.session.get(PostRow, int(obj.id))
        if row is None:
            raise NotFoundPostError(POST_NOT_FOUND)
        row.title = obj.title.value
        row.body = obj.body.value
        row.tags = list(obj.tags.values)
        row.reactions_likes = obj.reactions_likes
        row.reactions_dislikes = obj.reactions_dislikes
        row.views = obj.views
        row.updated_at = obj.updated_at
        await self.session.flush()
        return post_row_to_model(row)

    async def get(
        self,
        id_: PostID | None = None,
        /,
        *,
        external_id: ExternalPostID | None = None,
    ) -> PostModel | None:
        stmt = select(PostRow)
        if id_ is not None:
            stmt = stmt.where(PostRow.id == int(id_))
        if external_id is not None:
            stmt = stmt.where(PostRow.external_id == int(external_id))
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return None
        return post_row_to_model(row)

    async def delete(self, id_: PostID, /) -> None:
        row = await self.session.get(PostRow, int(id_))
        if row is None:
            raise NotFoundPostError(POST_NOT_FOUND)
        await self.session.delete(row)
        await self.session.flush()

    async def list_(
        self,
        *,
        page: PageRequest,
        author_id: UserID | None = None,
    ) -> Page[PostModel]:
        if page.sort.field not in self.SORTABLE_FIELDS:
            raise ValidationError(f"unsortable field: {page.sort.field}")

        column = _SORT_COLUMNS[page.sort.field]
        order = column.asc() if page.sort.direction == SortDirection.ASC else column.desc()

        count_stmt = select(func.count()).select_from(PostRow)
        list_stmt = select(PostRow).order_by(order, PostRow.id.asc())
        if author_id is not None:
            count_stmt = count_stmt.where(PostRow.user_id == int(author_id))
            list_stmt = list_stmt.where(PostRow.user_id == int(author_id))

        total = (await self.session.execute(count_stmt)).scalar_one()
        list_stmt = list_stmt.limit(page.limit).offset(page.offset)
        rows = (await self.session.execute(list_stmt)).scalars().all()

        return Page[PostModel](
            items=[post_row_to_model(r) for r in rows],
            total=int(total),
            limit=page.limit,
            offset=page.offset,
        )

    async def upsert_by_external_id(
        self, data: NewPostData, /, *, now: datetime
    ) -> tuple[PostModel, bool]:
        if data.external_id is None:
            raise ValidationError("upsert_by_external_id requires external_id")

        existing = (
            await self.session.execute(
                select(PostRow).where(PostRow.external_id == int(data.external_id))
            )
        ).scalar_one_or_none()

        if existing is None:
            row = PostRow(
                external_id=int(data.external_id),
                user_id=int(data.user_id),
                title=data.title.value,
                body=data.body.value,
                tags=list(data.tags.values),
                reactions_likes=data.reactions_likes,
                reactions_dislikes=data.reactions_dislikes,
                views=data.views,
                created_at=now,
                updated_at=now,
            )
            self.session.add(row)
            try:
                await self.session.flush()
            except IntegrityError as e:
                await self.session.rollback()
                self._translate_fk_violation(e)
                raise
            await self.session.refresh(row)
            return post_row_to_model(row), True

        changed = (
            existing.user_id != int(data.user_id)
            or existing.title != data.title.value
            or existing.body != data.body.value
            or list(existing.tags) != list(data.tags.values)
            or existing.reactions_likes != data.reactions_likes
            or existing.reactions_dislikes != data.reactions_dislikes
            or existing.views != data.views
        )
        if changed:
            existing.user_id = int(data.user_id)
            existing.title = data.title.value
            existing.body = data.body.value
            existing.tags = list(data.tags.values)
            existing.reactions_likes = data.reactions_likes
            existing.reactions_dislikes = data.reactions_dislikes
            existing.views = data.views
            existing.updated_at = now
            await self.session.flush()
        return post_row_to_model(existing), False

    @staticmethod
    def _translate_fk_violation(e: IntegrityError) -> None:
        message = str(e.orig).lower() if e.orig is not None else str(e).lower()
        if "foreign key" in message or "fk_posts_user_id" in message or "user_id" in message:
            raise PostAuthorNotFoundError(POST_AUTHOR_NOT_FOUND) from e
