from datetime import datetime

from domain.entities import AggregateRoot, ValueObject
from domain.ids import ExternalPostID, PostID, UserID
from domain.post.value_objects import Body, Tags, Title


class PostModel(AggregateRoot):
    id: PostID
    external_id: ExternalPostID | None = None
    user_id: UserID
    title: Title
    body: Body
    tags: Tags
    reactions_likes: int = 0
    reactions_dislikes: int = 0
    views: int = 0
    created_at: datetime
    updated_at: datetime

    def edit(
        self,
        *,
        title: Title | None,
        body: Body | None,
        tags: Tags | None,
        now: datetime,
    ) -> "PostModel":
        new_title = title if title is not None else self.title
        new_body = body if body is not None else self.body
        new_tags = tags if tags is not None else self.tags
        if new_title == self.title and new_body == self.body and new_tags == self.tags:
            return self
        return self.model_copy(
            update={"title": new_title, "body": new_body, "tags": new_tags, "updated_at": now}
        )


class NewPostData(ValueObject):
    external_id: ExternalPostID | None = None
    user_id: UserID
    title: Title
    body: Body
    tags: Tags
    reactions_likes: int = 0
    reactions_dislikes: int = 0
    views: int = 0
