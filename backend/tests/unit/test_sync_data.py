import pytest

from domain.ids import ExternalUserID
from domain.sync.use_cases import SyncDataUseCaseImpl
from tests.fakes.clock import FakeClock
from tests.fakes.dummyjson import StubDummyJSONClient
from tests.fakes.unit_of_work import FakeUnitOfWork

pytestmark = pytest.mark.unit


def _make_use_case(
    *,
    uow: FakeUnitOfWork,
    client: StubDummyJSONClient,
    clock: FakeClock,
) -> SyncDataUseCaseImpl:
    return SyncDataUseCaseImpl(uow=uow, user_source=client, post_source=client, clock=clock)


async def test_sync_persists_users_and_posts(
    fake_uow, fake_clock, sample_remote_users, sample_remote_posts
):
    client = StubDummyJSONClient(users=sample_remote_users, posts=sample_remote_posts)
    use_case = _make_use_case(uow=fake_uow, client=client, clock=fake_clock)

    result = await use_case()

    assert result.users_added == 2
    assert result.users_updated == 0
    assert result.posts_added == 1
    assert result.posts_skipped_missing_author == 1
    assert fake_uow.commit_calls == 1


async def test_sync_is_idempotent_on_second_run(
    fake_uow, fake_clock, sample_remote_users, sample_remote_posts
):
    client = StubDummyJSONClient(users=sample_remote_users, posts=sample_remote_posts)
    use_case = _make_use_case(uow=fake_uow, client=client, clock=fake_clock)

    first = await use_case()
    second = await use_case()

    assert first.users_added == 2
    assert second.users_added == 0
    assert second.users_updated == 2
    assert second.posts_added == 0
    assert second.posts_updated == 1
    user = await fake_uow.user_repository.get(external_id=ExternalUserID(1))
    assert user is not None
    assert int(user.external_id or 0) == 1


async def test_sync_updates_changed_user_fields(
    fake_uow, fake_clock, sample_remote_users, sample_remote_posts
):
    client = StubDummyJSONClient(users=sample_remote_users, posts=sample_remote_posts)
    await _make_use_case(uow=fake_uow, client=client, clock=fake_clock)()

    fake_clock.advance_seconds(60)
    sample_remote_users[0] = sample_remote_users[0].model_copy(update={"first_name": "Augusta"})
    client_v2 = StubDummyJSONClient(users=sample_remote_users, posts=sample_remote_posts)

    result = await _make_use_case(uow=fake_uow, client=client_v2, clock=fake_clock)()

    user = await fake_uow.user_repository.get(external_id=ExternalUserID(1))
    assert user is not None
    assert user.name.first == "Augusta"
    assert result.users_updated == 2
