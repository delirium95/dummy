from pydantic import BaseModel, ConfigDict

from domain.sync.dto import SyncResult


class SyncResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    users_added: int
    users_updated: int
    posts_added: int
    posts_updated: int
    posts_skipped_missing_author: int

    @classmethod
    def from_domain(cls, result: SyncResult) -> "SyncResultResponse":
        return cls(
            users_added=result.users_added,
            users_updated=result.users_updated,
            posts_added=result.posts_added,
            posts_updated=result.posts_updated,
            posts_skipped_missing_author=result.posts_skipped_missing_author,
        )
