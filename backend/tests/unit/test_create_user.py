import pytest

from domain.errors import EmailAlreadyExistsError
from domain.user.model import NewUserData
from domain.user.use_cases import CreateUserUseCaseImpl

pytestmark = pytest.mark.unit


async def test_create_user_persists_and_commits(
    fake_uow, fake_clock, make_email, make_name, make_username
):
    use_case = CreateUserUseCaseImpl(uow=fake_uow, clock=fake_clock)

    user = await use_case(
        NewUserData(name=make_name(), email=make_email(), username=make_username())
    )

    assert int(user.id) > 0
    assert user.created_at == fake_clock.now()
    assert fake_uow.commit_calls == 1
    stored = await fake_uow.user_repository.get(user.id)
    assert stored is not None and stored.email == user.email


async def test_create_user_rejects_duplicate_email(
    fake_uow, fake_clock, make_email, make_name, make_username
):
    use_case = CreateUserUseCaseImpl(uow=fake_uow, clock=fake_clock)
    await use_case(
        NewUserData(name=make_name(), email=make_email("same@x.com"), username=make_username("u1"))
    )

    with pytest.raises(EmailAlreadyExistsError):
        await use_case(
            NewUserData(
                name=make_name(first="A", last="B"),
                email=make_email("same@x.com"),
                username=make_username("u2"),
            )
        )
