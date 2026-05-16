from pydantic import BaseModel, ConfigDict, Field


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=False, populate_by_name=True)


class RemoteUserPayload(_StrictModel):
    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str
    username: str


class _RemotePostReactions(_StrictModel):
    likes: int = 0
    dislikes: int = 0


class RemotePostPayload(_StrictModel):
    id: int
    user_id: int = Field(alias="userId")
    title: str
    body: str
    tags: list[str] = Field(default_factory=list)
    reactions: _RemotePostReactions = Field(default_factory=_RemotePostReactions)
    views: int = 0


class UsersListPayload(_StrictModel):
    users: list[RemoteUserPayload]
    total: int
    skip: int
    limit: int


class PostsListPayload(_StrictModel):
    posts: list[RemotePostPayload]
    total: int
    skip: int
    limit: int
