import httpx
from dependency_injector import containers, providers

from config.settings import Settings
from domain.post.use_cases import (
    CreatePostUseCaseImpl,
    DeletePostUseCaseImpl,
    GetPostUseCaseImpl,
    ListPostsUseCaseImpl,
    UpdatePostUseCaseImpl,
)
from domain.sync.use_cases import SyncDataUseCaseImpl
from domain.user.use_cases import (
    CreateUserUseCaseImpl,
    DeleteUserUseCaseImpl,
    GetUserUseCaseImpl,
    ListUsersUseCaseImpl,
    UpdateUserUseCaseImpl,
)
from infrastructure.clock import SystemClock
from infrastructure.database.session import make_engine, make_session_maker
from infrastructure.dummyjson.client import DummyJSONClient
from repositories.unit_of_work import SQLAlchemyUnitOfWork


async def _httpx_client_resource(base_url: str, timeout_seconds: float):
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout_seconds) as client:
        yield client


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.routers.users",
            "api.routers.posts",
            "api.routers.sync",
        ]
    )

    settings: providers.Singleton[Settings] = providers.Singleton(Settings)

    engine = providers.Singleton(make_engine, database_url=settings.provided.database_url)
    session_maker = providers.Singleton(make_session_maker, engine=engine)

    clock = providers.Singleton(SystemClock)

    http_client: providers.Resource[httpx.AsyncClient] = providers.Resource(
        _httpx_client_resource,
        base_url=settings.provided.dummyjson_base_url,
        timeout_seconds=settings.provided.dummyjson_timeout_seconds,
    )

    dummyjson_client = providers.Singleton(DummyJSONClient, http_client=http_client)

    uow = providers.Factory(SQLAlchemyUnitOfWork, session_maker=session_maker)

    list_users_use_case = providers.Factory(ListUsersUseCaseImpl, uow=uow)
    get_user_use_case = providers.Factory(GetUserUseCaseImpl, uow=uow)
    create_user_use_case = providers.Factory(CreateUserUseCaseImpl, uow=uow, clock=clock)
    update_user_use_case = providers.Factory(UpdateUserUseCaseImpl, uow=uow, clock=clock)
    delete_user_use_case = providers.Factory(DeleteUserUseCaseImpl, uow=uow)

    list_posts_use_case = providers.Factory(ListPostsUseCaseImpl, uow=uow)
    get_post_use_case = providers.Factory(GetPostUseCaseImpl, uow=uow)
    create_post_use_case = providers.Factory(CreatePostUseCaseImpl, uow=uow, clock=clock)
    update_post_use_case = providers.Factory(UpdatePostUseCaseImpl, uow=uow, clock=clock)
    delete_post_use_case = providers.Factory(DeletePostUseCaseImpl, uow=uow)

    sync_data_use_case = providers.Factory(
        SyncDataUseCaseImpl,
        uow=uow,
        user_source=dummyjson_client,
        post_source=dummyjson_client,
        clock=clock,
    )
