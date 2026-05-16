from datetime import datetime

from domain.error_messages import POST_NOT_FOUND
from domain.errors import NotFoundPostError, ValidationError
from domain.ids import ExternalPostID, PostID, UserID
from domain.post.interfaces import PostRepository
from domain.post.model import NewPostData, PostModel
from domain.shared.pagination import Page, PageRequest, SortDirection


class InMemoryPostRepository(PostRepository):
    def __init__(self) -> None:
        self._posts: dict[int, PostModel] = {}
        self._next_id = 1

    async def add(self, obj: PostModel, /) -> PostModel:
        self._posts[int(obj.id)] = obj
        self._next_id = max(self._next_id, int(obj.id) + 1)
        return obj

    async def create(self, data: NewPostData, /, *, now: datetime) -> PostModel:
        post_id = PostID(self._next_id)
        self._next_id += 1
        post = PostModel(
            id=post_id,
            external_id=data.external_id,
            user_id=data.user_id,
            title=data.title,
            body=data.body,
            tags=data.tags,
            reactions_likes=data.reactions_likes,
            reactions_dislikes=data.reactions_dislikes,
            views=data.views,
            created_at=now,
            updated_at=now,
        )
        self._posts[int(post_id)] = post
        return post

    async def update(self, obj: PostModel, /) -> PostModel:
        if int(obj.id) not in self._posts:
            raise NotFoundPostError(POST_NOT_FOUND)
        self._posts[int(obj.id)] = obj
        return obj

    async def get(
        self,
        id_: PostID | None = None,
        /,
        *,
        external_id: ExternalPostID | None = None,
    ) -> PostModel | None:
        for post in self._posts.values():
            if id_ is not None and int(post.id) != int(id_):
                continue
            if external_id is not None and (
                post.external_id is None or int(post.external_id) != int(external_id)
            ):
                continue
            return post
        return None

    async def delete(self, id_: PostID, /) -> None:
        if int(id_) not in self._posts:
            raise NotFoundPostError(POST_NOT_FOUND)
        del self._posts[int(id_)]

    async def list_(
        self,
        *,
        page: PageRequest,
        author_id: UserID | None = None,
    ) -> Page[PostModel]:
        if page.sort.field not in self.SORTABLE_FIELDS:
            raise ValidationError(f"unsortable field: {page.sort.field}")
        items = [
            p for p in self._posts.values() if author_id is None or int(p.user_id) == int(author_id)
        ]
        items.sort(
            key=self._sort_key(page.sort.field),
            reverse=page.sort.direction == SortDirection.DESC,
        )
        sliced = items[page.offset : page.offset + page.limit]
        return Page[PostModel](items=sliced, total=len(items), limit=page.limit, offset=page.offset)

    async def upsert_by_external_id(
        self, data: NewPostData, /, *, now: datetime
    ) -> tuple[PostModel, bool]:
        if data.external_id is None:
            raise ValidationError("upsert_by_external_id requires external_id")
        existing = await self.get(external_id=data.external_id)
        if existing is None:
            return await self.create(data, now=now), True
        updated = existing.model_copy(
            update={
                "user_id": data.user_id,
                "title": data.title,
                "body": data.body,
                "tags": data.tags,
                "reactions_likes": data.reactions_likes,
                "reactions_dislikes": data.reactions_dislikes,
                "views": data.views,
                "updated_at": now,
            }
        )
        self._posts[int(existing.id)] = updated
        return updated, False

    @staticmethod
    def _sort_key(field: str):
        def key(p: PostModel):
            match field:
                case "id":
                    return int(p.id)
                case "title":
                    return p.title.value
                case "user_id":
                    return int(p.user_id)
                case "views":
                    return p.views
                case "reactions_likes":
                    return p.reactions_likes
                case "created_at":
                    return p.created_at
                case _:
                    return int(p.id)

        return key
