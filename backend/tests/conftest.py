import pytest

from domain.ids import ExternalUserID
from domain.sync.dto import RemotePost, RemoteUser
from domain.user.value_objects import Email, FullName, Username
from tests.fakes.clock import FakeClock
from tests.fakes.dummyjson import StubDummyJSONClient
from tests.fakes.unit_of_work import FakeUnitOfWork


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def stub_dummyjson_client() -> StubDummyJSONClient:
    return StubDummyJSONClient()


@pytest.fixture
def sample_remote_users() -> list[RemoteUser]:
    return [
        RemoteUser(
            external_id=1,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            username="ada",
        ),
        RemoteUser(
            external_id=2,
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
            username="grace",
        ),
    ]


@pytest.fixture
def sample_remote_posts() -> list[RemotePost]:
    return [
        RemotePost(
            external_id=10,
            user_external_id=1,
            title="On analytical engines",
            body="A note on the analytical engine",
            tags=("history", "math"),
            reactions_likes=5,
            reactions_dislikes=0,
            views=100,
        ),
        RemotePost(
            external_id=11,
            user_external_id=999,
            title="Orphaned post",
            body="No matching author",
            tags=(),
            reactions_likes=0,
            reactions_dislikes=0,
            views=0,
        ),
    ]


@pytest.fixture
def make_email():
    def _make(value: str = "user@example.com") -> Email:
        return Email(value=value)

    return _make


@pytest.fixture
def make_name():
    def _make(first: str = "Test", last: str = "User") -> FullName:
        return FullName(first=first, last=last)

    return _make


@pytest.fixture
def make_username():
    def _make(value: str = "tester") -> Username:
        return Username(value=value)

    return _make


@pytest.fixture
def make_external_user_id():
    def _make(value: int = 1) -> ExternalUserID:
        return ExternalUserID(value)

    return _make
