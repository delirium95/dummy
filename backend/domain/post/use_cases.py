from domain.error_messages import POST_NOT_FOUND
from domain.errors import NotFoundPostError
from domain.ids import PostID, UserID
from domain.post.interfaces import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetPostUseCase,
    ListPostsUseCase,
    UpdatePostUseCase,
)
from domain.post.model import NewPostData, PostModel
from domain.post.value_objects import Body, Tags, Title
from domain.shared.clock import Clock
from domain.shared.pagination import Page, PageRequest
from domain.unit_of_work import UnitOfWork


class ListPostsUseCaseImpl(ListPostsUseCase):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def __call__(self, page: PageRequest, author_id: UserID | None = None) -> Page[PostModel]:
        async with self.uow as uow:
            return await uow.post_repository.list_(page=page, author_id=author_id)


class GetPostUseCaseImpl(GetPostUseCase):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def __call__(self, post_id: PostID) -> PostModel:
        async with self.uow as uow:
            post = await uow.post_repository.get(post_id)
            if post is None:
                raise NotFoundPostError(POST_NOT_FOUND)
            return post


class CreatePostUseCaseImpl(CreatePostUseCase):
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self.uow = uow
        self.clock = clock

    async def __call__(self, data: NewPostData) -> PostModel:
        async with self.uow as uow:
            created = await uow.post_repository.create(data, now=self.clock.now())
            await uow.commit()
            return created


class UpdatePostUseCaseImpl(UpdatePostUseCase):
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self.uow = uow
        self.clock = clock

    async def __call__(
        self,
        post_id: PostID,
        *,
        title: Title | None = None,
        body: Body | None = None,
        tags: Tags | None = None,
    ) -> PostModel:
        now = self.clock.now()
        async with self.uow as uow:
            current = await uow.post_repository.get(post_id)
            if current is None:
                raise NotFoundPostError(POST_NOT_FOUND)
            updated = current.edit(title=title, body=body, tags=tags, now=now)
            if updated is current:
                return current
            persisted = await uow.post_repository.update(updated)
            await uow.commit()
            return persisted


class DeletePostUseCaseImpl(DeletePostUseCase):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def __call__(self, post_id: PostID) -> None:
        async with self.uow as uow:
            await uow.post_repository.delete(post_id)
            await uow.commit()
