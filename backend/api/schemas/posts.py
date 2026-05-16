from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from domain.ids import UserID
from domain.post.model import NewPostData, PostModel
from domain.post.value_objects import Body, Tags, Title


class PostResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    external_id: int | None
    user_id: int
    title: str
    body: str
    tags: list[str]
    reactions_likes: int
    reactions_dislikes: int
    views: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, post: PostModel) -> "PostResponse":
        return cls(
            id=int(post.id),
            external_id=int(post.external_id) if post.external_id is not None else None,
            user_id=int(post.user_id),
            title=post.title.value,
            body=post.body.value,
            tags=list(post.tags.values),
            reactions_likes=post.reactions_likes,
            reactions_dislikes=post.reactions_dislikes,
            views=post.views,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )


class CreatePostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)

    def to_domain(self) -> NewPostData:
        return NewPostData(
            user_id=UserID(self.user_id),
            title=Title(value=self.title),
            body=Body(value=self.body),
            tags=Tags(values=tuple(self.tags)),
        )


class UpdatePostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=500)
    body: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None

    def title_or_none(self) -> Title | None:
        return Title(value=self.title) if self.title is not None else None

    def body_or_none(self) -> Body | None:
        return Body(value=self.body) if self.body is not None else None

    def tags_or_none(self) -> Tags | None:
        return Tags(values=tuple(self.tags)) if self.tags is not None else None
