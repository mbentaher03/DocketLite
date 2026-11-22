# DocketLite
Small FastAPI + PostgreSQL items API used to demonstrate a complete DevOps chain: Git workflow,
Bash checks, Docker, Compose, CI, tagged releases, deployment and rollback.
## Quick start (one command)
    docker compose up -d --build
Then open http://localhost:8080/health (expected: {"status":"ok","db":"ok"}).
Stop with `docker compose down` (keeps data) or `docker compose down -v` (deletes data).
## Run the checks
    ./scripts/check.sh            # unit tests
    ./scripts/check.sh --live     # unit tests + live /health check
## API
GET /health, GET /version, GET /items, POST /items with {"title": "...", "description": "..."}
## Architecture
api (FastAPI, port 8080) -> db (postgres:17-alpine) on a private Compose network.
Port 5432 is not published. Data lives in the named volume `pgdata`.
The API starts only when the database healthcheck passes.
## CI/CD
- Pull request: job `test` (pytest, JUnit artifact) then job `docker-build` (needs: test).
- Tag `v*`: workflow Release builds the image once and pushes ghcr.io/mbentaher03/docketlite:TAG.
## Deploy and roll back (staging)
    ./scripts/deploy.sh v1.0.1     # deploy a published version
    ./scripts/deploy.sh v1.0.0     # roll back to the previous version
## Pipeline evidence
- Successful run: https://github.com/mbentaher03/DocketLite/actions/runs/45051806926
- Failed run: https://github.com/mbentaher03/DocketLite/actions/runs/45053036997
## Credentials
The default database password `docketlite_pass` is fictional and for local use only.
