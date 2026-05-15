# dummyjson-sync

Small full-stack app that syncs users and posts from
[dummyjson.com](https://dummyjson.com) into Postgres and exposes them via a
REST API and a React UI.

Run the whole stack with a single command:

```bash
docker compose up --build
```

- Backend: http://localhost:8000 (Swagger at `/docs`)
- Frontend: http://localhost:8080

See [docs/architecture.md](docs/architecture.md) for the architecture notes.
