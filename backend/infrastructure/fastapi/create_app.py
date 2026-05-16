from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import register_exception_handlers
from api.routers import posts as posts_router
from api.routers import sync as sync_router
from api.routers import users as users_router
from containers import Container


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    container: Container = app.state.container
    await container.init_resources()
    try:
        yield
    finally:
        await container.shutdown_resources()


def create_app() -> FastAPI:
    container = Container()
    settings = container.settings()

    app = FastAPI(
        title="DummyJSON Sync API",
        version="0.1.0",
        lifespan=_lifespan,
    )
    app.state.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(users_router.router)
    app.include_router(posts_router.router)
    app.include_router(sync_router.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
