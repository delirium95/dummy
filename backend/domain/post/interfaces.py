from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from domain.common.repository import AbstractRepository
from domain.ids import ExternalPostID, PostID, UserID
from domain.post.model import NewPostData, PostModel
from domain.post.value_objects import Body, Tags, Title
from domain.shared.pagination import Page, PageRequest


class PostRepository(AbstractRepository[PostID, PostModel]):
    SORTABLE_FIELDS: frozenset[str] = frozenset(
        {"id", "title", "user_id", "views", "reactions_likes", "created_at"}
    )

    @abstractmethod
    async def add(self, obj: PostModel, /) -> PostModel: ...

    @abstractmethod
    async def create(self, data: NewPostData, /, *, now: datetime) -> PostModel: ...

    @abstractmethod
    async def update(self, obj: PostModel, /) -> PostModel: ...

    @abstractmethod
    async def get(
        self,
        id_: PostID | None = None,
        /,
        *,
        external_id: ExternalPostID | None = None,
    ) -> PostModel | None: ...

    @abstractmethod
    async def delete(self, id_: PostID, /) -> None: ...

    @abstractmethod
    async def list_(
        self,
        *,
        page: PageRequest,
        author_id: UserID | None = None,
    ) -> Page[PostModel]: ...

    @abstractmethod
    async def upsert_by_external_id(
        self, data: NewPostData, /, *, now: datetime
    ) -> tuple[PostModel, bool]: ...


class ListPostsUseCase(Protocol):
    async def __call__(
        self, page: PageRequest, author_id: UserID | None = None
    ) -> Page[PostModel]: ...


class GetPostUseCase(Protocol):
    async def __call__(self, post_id: PostID) -> PostModel: ...


class CreatePostUseCase(Protocol):
    async def __call__(self, data: NewPostData) -> PostModel: ...


class UpdatePostUseCase(Protocol):
    async def __call__(
        self,
        post_id: PostID,
        *,
        title: Title | None = None,
        body: Body | None = None,
        tags: Tags | None = None,
    ) -> PostModel: ...


class DeletePostUseCase(Protocol):
    async def __call__(self, post_id: PostID) -> None: ...
