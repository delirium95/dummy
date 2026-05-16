from domain.ids import ExternalPostID, ExternalUserID, UserID
from domain.post.model import NewPostData
from domain.post.value_objects import Body, Tags, Title
from domain.shared.clock import Clock
from domain.sync.dto import RemotePost, RemoteUser, SyncResult
from domain.sync.interfaces import ExternalPostSource, ExternalUserSource, SyncDataUseCase
from domain.unit_of_work import UnitOfWork
from domain.user.model import NewUserData
from domain.user.value_objects import Email, FullName, Username


class SyncDataUseCaseImpl(SyncDataUseCase):
    def __init__(
        self,
        uow: UnitOfWork,
        user_source: ExternalUserSource,
        post_source: ExternalPostSource,
        clock: Clock,
    ) -> None:
        self.uow = uow
        self.user_source = user_source
        self.post_source = post_source
        self.clock = clock

    async def __call__(self) -> SyncResult:
        remote_users = await self.user_source.fetch_users()
        remote_posts = await self.post_source.fetch_posts()
        now = self.clock.now()

        users_added = 0
        users_updated = 0
        posts_added = 0
        posts_updated = 0
        posts_skipped_missing_author = 0

        async with self.uow as uow:
            external_to_internal: dict[int, UserID] = {}
            for remote in remote_users:
                user_data = _to_new_user_data(remote)
                user, created = await uow.user_repository.upsert_by_external_id(user_data, now=now)
                external_to_internal[remote.external_id] = user.id
                if created:
                    users_added += 1
                else:
                    users_updated += 1

            for remote in remote_posts:
                author_id = external_to_internal.get(remote.user_external_id)
                if author_id is None:
                    posts_skipped_missing_author += 1
                    continue
                post_data = _to_new_post_data(remote, author_id)
                _, created = await uow.post_repository.upsert_by_external_id(post_data, now=now)
                if created:
                    posts_added += 1
                else:
                    posts_updated += 1

            await uow.commit()

        return SyncResult(
            users_added=users_added,
            users_updated=users_updated,
            posts_added=posts_added,
            posts_updated=posts_updated,
            posts_skipped_missing_author=posts_skipped_missing_author,
        )


def _to_new_user_data(remote: RemoteUser) -> NewUserData:
    return NewUserData(
        external_id=ExternalUserID(remote.external_id),
        name=FullName(first=remote.first_name, last=remote.last_name),
        email=Email(value=remote.email),
        username=Username(value=remote.username),
    )


def _to_new_post_data(remote: RemotePost, author_id: UserID) -> NewPostData:
    return NewPostData(
        external_id=ExternalPostID(remote.external_id),
        user_id=author_id,
        title=Title(value=remote.title),
        body=Body(value=remote.body),
        tags=Tags(values=remote.tags),
        reactions_likes=remote.reactions_likes,
        reactions_dislikes=remote.reactions_dislikes,
        views=remote.views,
    )
