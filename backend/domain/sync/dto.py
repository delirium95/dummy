from domain.entities import ValueObject


class RemoteUser(ValueObject):
    external_id: int
    first_name: str
    last_name: str
    email: str
    username: str


class RemotePost(ValueObject):
    external_id: int
    user_external_id: int
    title: str
    body: str
    tags: tuple[str, ...]
    reactions_likes: int
    reactions_dislikes: int
    views: int


class SyncResult(ValueObject):
    users_added: int
    users_updated: int
    posts_added: int
    posts_updated: int
    posts_skipped_missing_author: int
