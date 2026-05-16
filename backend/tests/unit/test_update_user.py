import pytest

from domain.errors import NotFoundUserError
from domain.ids import UserID
from domain.user.model import NewUserData
from domain.user.use_cases import CreateUserUseCaseImpl, UpdateUserUseCaseImpl

pytestmark = pytest.mark.unit


async def test_update_user_renames_and_bumps_updated_at(
    fake_uow, fake_clock, make_email, make_name, make_username
):
    created = await CreateUserUseCaseImpl(uow=fake_uow, clock=fake_clock)(
        NewUserData(name=make_name(), email=make_email(), username=make_username())
    )
    fake_clock.advance_seconds(120)

    updated = await UpdateUserUseCaseImpl(uow=fake_uow, clock=fake_clock)(
        created.id, name=make_name(first="Augusta", last="Lovelace")
    )

    assert updated.name.first == "Augusta"
    assert updated.updated_at == fake_clock.now()
    assert updated.created_at == created.created_at


async def test_update_user_raises_when_missing(fake_uow, fake_clock, make_name):
    with pytest.raises(NotFoundUserError):
        await UpdateUserUseCaseImpl(uow=fake_uow, clock=fake_clock)(
            UserID(9999), name=make_name(first="A", last="B")
        )
