# dummyjson-sync

Small full-stack app that ingests **users** and **posts** from
[dummyjson.com](https://dummyjson.com) into Postgres and exposes them via a
FastAPI REST API and a React UI.

## Run

```bash
docker compose up --build
```

That single command brings up:

| Service  | URL                        | Notes                                |
| -------- | -------------------------- | ------------------------------------ |
| backend  | http://localhost:8000      | Swagger UI at `/docs`                |
| frontend | http://localhost:8080      | Static build served via nginx        |
| db       | _internal_                 | Postgres 16, reachable at `db:5432` inside the compose network |

Migrations run automatically on backend startup
(`alembic upgrade head`), so the schema is in place before the API listens.

Trigger an initial sync from the UI (button **Sync from DummyJSON**) or via:

```bash
curl -X POST http://localhost:8000/sync
```

## Stack

- **Backend** — Python 3.12, FastAPI, SQLAlchemy 2.x async, asyncpg, Alembic,
  Pydantic v2, dependency-injector, httpx.
- **Frontend** — React 18, TypeScript strict mode, Vite, Redux Toolkit Query.
- **DB** — Postgres 16.

## Architecture

The backend follows DDD / clean architecture with strict inward-only
dependency flow:

```
infrastructure → adapters (api/, repositories/) → application (use_cases) → domain
```

### Layers

```
backend/
├── domain/                  # pure: entities, value objects, interfaces, use cases
│   ├── entities.py          # ValueObject / Entity / AggregateRoot (pydantic v2)
│   ├── ids.py               # NewType identifiers
│   ├── errors.py            # DomainError hierarchy
│   ├── error_messages.py
│   ├── common/repository.py # AbstractRepository[Identity, Aggregate]
│   ├── shared/              # Clock, UoW, pagination (cross-cutting)
│   ├── unit_of_work.py      # typed UoW exposing user/post repositories
│   ├── user/, post/, sync/  # one folder per aggregate:
│   │   ├── model.py         #   AggregateRoot + NewXData VO
│   │   ├── value_objects.py #   Email, FullName, Username, Title, Body, Tags
│   │   ├── interfaces.py    #   Repository ABC + UseCase Protocols
│   │   └── use_cases.py     #   *UseCaseImpl classes orchestrating the UoW
├── repositories/            # SQLAlchemy implementations of domain repositories
├── infrastructure/          # external adapters (DB session, httpx, clock, FastAPI)
├── api/                     # FastAPI routers + Pydantic request/response schemas
├── containers.py            # dependency-injector wiring
├── config/settings.py       # pydantic-settings (env-based)
├── alembic/                 # migrations
└── tests/                   # unit tests with in-memory fakes and respx
```

### Key decisions

- **Rich domain model.** Entities (`UserModel`, `PostModel`) carry behaviour
  (`rename`, `change_email`, `edit`, …). Value objects (`Email`, `FullName`,
  `Title`, `Tags`) validate at construction — invariants live in the type
  system, not in services.
- **Repository + Unit of Work.** Repositories return domain entities (never
  ORM rows). All writes inside a use case run within `async with self.uow as
  uow:` followed by `await uow.commit()`. Tests swap the UoW for a
  `FakeUnitOfWork` with `InMemoryUserRepository` / `InMemoryPostRepository`.
- **External world is a port.** `ExternalUserSource` /
  `ExternalPostSource` live in `domain/sync/interfaces.py`; the httpx-based
  `DummyJSONClient` is the only place that talks to the network. Timeouts and
  non-2xx are translated into domain errors
  (`ExternalSourceTimeoutError`, `ExternalSourceUnavailableError`,
  `ExternalSourcePayloadError`).
- **Idempotent sync.** Users and posts carry an `external_id` with a unique
  index. The sync use case upserts by `external_id`; running it twice yields
  zero new rows.
- **Exception handlers** in `api/errors.py` map domain errors to RFC-ish
  problem responses:
  - `NotFoundError` → 404
  - `ConflictError` → 409
  - `ValidationError` → 400
  - `ExternalSourceTimeoutError` → 504
  - `ExternalSourceUnavailableError` / `ExternalSourcePayloadError` → 502
- **Async all the way.** No blocking I/O inside async paths — asyncpg driver,
  `AsyncSession`, `httpx.AsyncClient`, `async with uow`.
- **DI.** `containers.py` exposes use cases as `providers.Factory`; FastAPI
  endpoints receive them through `Depends(Provide[...])`.
- **Frontend** is a single page (`UsersPage`) with sortable columns,
  offset/limit pagination, edit/create modals with client-side validation,
  delete confirmation, a per-user posts modal (list / create / edit / delete),
  and explicit loading/error/empty states. All HTTP lives in
  `src/services/api.ts` (Redux Toolkit Query) with the store wired in
  `src/store/store.ts` — components only consume generated hooks
  (`useGetUsersQuery`, `useCreateUserMutation`, …) and never touch `fetch`
  directly. Cache invalidation by tag (`User` / `Post`, with `LIST` and
  `USER-<id>` scopes) keeps the table in sync after mutations and syncs.

## API

| Method  | Path                       | Description                            |
| ------- | -------------------------- | -------------------------------------- |
| GET     | `/users`                   | List users (limit/offset/sort/direction) |
| GET     | `/users/{id}`              | Get user with embedded posts           |
| GET     | `/users/{id}/posts`        | List posts of a given user             |
| POST    | `/users`                   | Create user                            |
| PUT     | `/users/{id}`              | Update user                            |
| DELETE  | `/users/{id}`              | Delete user                            |
| GET     | `/posts`                   | List posts                             |
| GET     | `/posts/{id}`              | Get post with embedded author          |
| GET     | `/posts/{id}/author`       | Get the related author                 |
| POST    | `/posts`                   | Create post                            |
| PUT     | `/posts/{id}`              | Update post                            |
| DELETE  | `/posts/{id}`              | Delete post                            |
| POST    | `/sync`                    | Idempotent sync from DummyJSON         |
| GET     | `/health`                  | Liveness                               |

Allowed sort fields are enforced by the repository
(`UserRepository.SORTABLE_FIELDS`, `PostRepository.SORTABLE_FIELDS`); an
invalid sort returns 400 instead of leaking an ORM error.

## Tests

```bash
cd backend
uv sync --frozen
uv run pytest
```

Suites:

- `tests/unit/test_sync_data.py` — sync persistence, idempotence on second
  run, mutation detection.
- `tests/unit/test_create_user.py` — create flow + uniqueness conflict.
- `tests/unit/test_update_user.py` — partial update + not-found.
- `tests/unit/test_dummyjson_client.py` — happy path, 5xx, timeout, payload
  mismatch (uses `respx` to mock httpx).

Tests run against in-memory fakes (`tests/fakes/`) rather than a real DB; the
external HTTP boundary is mocked with `respx`. No network or DB needed.

## Configuration

All runtime settings come from environment variables (see
`backend/.env.example`):

| Variable                    | Default                                                  |
| --------------------------- | -------------------------------------------------------- |
| `DATABASE_URL`              | `postgresql+asyncpg://app:app@localhost:5433/dummyjson`  |
| `DUMMYJSON_BASE_URL`        | `https://dummyjson.com`                                  |
| `DUMMYJSON_TIMEOUT_SECONDS` | `10`                                                     |
| `CORS_ORIGINS`              | `["http://localhost:5173","http://localhost:8080"]`      |
| `LOG_LEVEL`                 | `INFO`                                                   |

Frontend reads `VITE_API_BASE_URL` at build time (see
`frontend/.env.example`).

## Code style

- **Python**: `ruff format` + `black` (line length 100).
- **TypeScript**: `prettier` (single quotes, trailing commas).
- `tsconfig.json` uses `strict`, `noImplicitAny`, `noUncheckedIndexedAccess`,
  `exactOptionalPropertyTypes`, `verbatimModuleSyntax` — there are no `any`s
  in the codebase.

### pre-commit

Hooks live in `.pre-commit-config.yaml` (Black, Ruff, Prettier, plus
trailing-whitespace / EOF / merge-conflict / large-file checks). Install
once after cloning:

```bash
cd backend && uv sync             # pulls pre-commit into the dev group
uv run pre-commit install         # registers the git hook
uv run pre-commit run --all-files # optional one-off run
```

## Repository layout

```
.
├── backend/        # FastAPI service (DDD layers above)
├── frontend/       # React + Vite SPA
├── docker-compose.yml
└── README.md
```
