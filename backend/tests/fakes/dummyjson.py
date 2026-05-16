from domain.sync.dto import RemotePost, RemoteUser
from domain.sync.interfaces import ExternalPostSource, ExternalUserSource


class StubDummyJSONClient(ExternalUserSource, ExternalPostSource):
    def __init__(
        self,
        users: list[RemoteUser] | None = None,
        posts: list[RemotePost] | None = None,
    ) -> None:
        self.users = users or []
        self.posts = posts or []
        self.fetch_users_calls = 0
        self.fetch_posts_calls = 0

    async def fetch_users(self) -> list[RemoteUser]:
        self.fetch_users_calls += 1
        return list(self.users)

    async def fetch_posts(self) -> list[RemotePost]:
        self.fetch_posts_calls += 1
        return list(self.posts)
