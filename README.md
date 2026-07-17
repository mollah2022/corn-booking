# Booking Sync Service

A modular data-synchronization system that pulls hotel booking data from an upstream API, transforms it according to business mapping rules, and persists it into PostgreSQL using an idempotent upsert strategy. Built with a clean separation between the data source (**API App**) and the sync worker (**Cron App**).

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Adding a New Cron Job](#adding-a-new-cron-job)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Scheduling](#scheduling)

## Architecture Overview

The system is composed of two independent processes that communicate over HTTP:

```
┌─────────────────┐         HTTP GET          ┌──────────────────┐
│   Cron App       │ ─────────────────────────▶│    API App        │
│   (app/)          │  /bookings?updated_from&  │   (api_app/)       │
│                    │   updated_to              │                    │
│  - Fetch           │◀───────────────────────── │  Flask + Redis     │
│  - Transform        │      JSON response         │  rate limiting     │
│  - Upsert to DB     │                            │                    │
└─────────────────┘                            └──────────────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL      │
│   (bookings table) │
└─────────────────┘
```

**API App** (`api_app/`) is a mock/stand-in data source built with Flask. It simulates an upstream provider (e.g. a hotel booking affiliate API) by serving JSON records filtered by an `updated_from` / `updated_to` date range. In production, this would be replaced by pointing the Cron App at a real upstream API — no other code changes required.

**Cron App** (`app/`) is a plain Python application (no web framework) responsible for the actual sync logic:

1. Fetch raw booking data from the API App via HTTP
2. Transform each record according to business mapping rules (status normalization, region lookup, currency conversion, label parsing)
3. Upsert the transformed records into PostgreSQL in chunks
4. Report the number of rows inserted/updated/failed

## Project Structure

```
booking_project/
├── main.py                          # Single entry point — dynamically loads and runs any cron job
├── docker-compose.yml                # Postgres, Redis, dbgate, test Postgres
├── settings.toml / .secrets.toml     # Environment-aware configuration (dynaconf)
├── pytest.ini / .coveragerc          # Test configuration
│
├── app/                              # Cron App — plain Python, no Flask
│   ├── db.py                         # SQLAlchemy engine + session_scope() context manager
│   ├── config/settings.py            # Dynaconf-based settings loader
│   ├── models/booking.py             # SQLAlchemy declarative model
│   ├── data/                         # Static mapping data (country→region, status map)
│   ├── services/
│   │   ├── common_service.py         # Reusable, config-free utilities
│   │   └── booking_service.py        # transform() and save_all() orchestration
│   ├── repositories/
│   │   └── booking_repository.py     # Chunked PostgreSQL UPSERT (ON CONFLICT DO UPDATE)
│   ├── api_client/
│   │   └── booking_api_client.py     # HTTP client with retry/backoff (tenacity)
│   └── cron/
│       └── booking.py                # BookingCron — orchestrates the full sync flow
│
├── api_app/                          # Mock data source — Flask app (port 5001)
│   ├── run.py
│   ├── data/
│   │   ├── mock_bookings.json        # Sample booking records
│   │   └── booking_loader.py
│   └── routes/
│       └── booking_routes.py         # /bookings endpoint, Redis-backed rate limiting
│
└── tests/                            # Mirrors the app/ structure 1:1
    ├── conftest.py                   # All fixtures live here
    ├── data/sample_booking.json
    ├── test_services/
    ├── test_repositories/
    ├── test_api_client/
    ├── test_cron/
    └── test_db.py
```

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- pip / venv

## Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/mollah2022/corn-booking.git
cd corn-booking

# 2. Start infrastructure (Postgres, Redis, dbgate, test Postgres)
docker-compose up -d

# 3. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy example config and adjust as needed
cp settings.toml.example settings.toml   # if using an example file
cp .secrets.toml.example .secrets.toml
```

## Configuration

Configuration is managed with [Dynaconf](https://www.dynaconf.com/), backed by two files:

| File | Purpose | Committed to git? |
|---|---|---|
| `settings.toml` | Non-sensitive settings (hosts, ports, URLs), environment-scoped (`[default]`, `[development]`, `[production]`, `[testing]`) | Yes |
| `.secrets.toml` | Sensitive values (passwords, API keys) | **No** (gitignored) |

Switch environments with:

```bash
export BOOKING_ENV=production
```

Key settings:

```toml
[default]
db_host = "localhost"
db_port = 5433
db_name = "booking_db"
db_user = "booking_user"
booking_api_base_url = "http://localhost:5001"
redis_host = "localhost"
redis_port = 6379
exchange_rate_api_base_url = "https://api.exchangerate-api.com/v4/latest"
```

## Running the Application

The **API App** must be running before any cron job is executed.

```bash
# Terminal 1 — start the mock/upstream API server
source venv/bin/activate
python -m api_app.run

# Terminal 2 — run a sync job
source venv/bin/activate
python main.py --job booking --from 2026-06-01 --to 2026-09-30
```

If `--from` / `--to` are omitted, the job defaults to the last 24 hours.

## Adding a New Cron Job

The system is designed so that adding a new sync job never requires touching existing code:

1. Create `app/cron/<job_name>.py` following the same class structure as `BookingCron` (`_resolve_date_range`, `_build_dependencies`, `_fetch_raw_bookings`, `_process_bookings`, `_report`, `run`).
2. Register it in `main.py`:
   ```python
   JOB_MODULE_MAP = {
       "booking": "app.cron.booking.BookingCron",
       "cars": "app.cron.cars.CarsCron",   # new job
   }
   ```
3. Add any supporting service/repository/API client files under the same folder pattern.
4. Add tests under `tests/test_cron/test_<job_name>_cron.py`, mirroring `test_booking_cron.py`.

Run it the same way as any other job:

```bash
python main.py --job cars --from 2026-06-01 --to 2026-09-30
```

## Testing

The project maintains **100% test coverage**. Tests are organized to mirror the `app/` package structure exactly, with all fixtures centralized in `tests/conftest.py`.

```bash
# Run the full suite with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
#multiple core
pytest tests/ -v --cov=app --cov-report=term-missing -n auto

# Enforce the coverage threshold (fails the build if coverage drops)
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=100

# Generate an HTML coverage report
pytest tests/ --cov=app --cov-report=html
```

**Testing approach:**

- **Unit tests** (`test_services/`) exercise pure business logic — mapping rules, transformation, chunking — with all external calls (exchange rate API) mocked via `unittest.mock` / `pytest-mock`.
- **Integration tests** (`test_repositories/`, `test_db.py`) run against a dedicated, ephemeral test PostgreSQL instance (`booking_test_postgres`, in-memory via `tmpfs`). Each test runs inside a transaction that is rolled back afterward, so tests never leak state into one another.
- **Orchestration tests** (`test_cron/`) mock every external dependency of `BookingCron` (API client, repository, service, DB session) to verify the control flow in isolation.

## Design Decisions

| Decision | Rationale |
|---|---|
| Cron App has no Flask dependency | It's a script, not a web server — plain Python + SQLAlchemy + a `session_scope()` context manager is simpler and has fewer moving parts. |
| PostgreSQL native `UPSERT` (`ON CONFLICT DO UPDATE`) | Avoids the select-then-branch race condition of manual insert/update logic and reduces round-trips. |
| Chunked writes (50 records/chunk) | Keeps memory and lock duration bounded on large batches while still batching DB round-trips (~7 commits for 350 records instead of 350). |
| Rate limiting on the exchange-rate API | Protects against exceeding the third-party provider's request limits; results are cached per run to minimize calls further. |
| Rate limiting on the API App (Redis-backed) | Works correctly across multiple server instances/workers, unlike in-memory rate limiting. |
| Retry with exponential backoff on API calls | Transient network failures shouldn't abort an entire sync cycle; failures are retried 3 times before raising. |
| `main.py` dynamic job loader | New sync jobs are added by registering a dotted class path — no existing code is modified (Open/Closed Principle). |

## Scheduling

For production, schedule the sync via system cron:

```bash
crontab -e
```

```
0 * * * * cd /path/to/booking_project && /path/to/booking_project/venv/bin/python main.py --job booking >> /path/to/booking_project/logs/cron.log 2>&1
```

## License

Internal project — license terms as applicable to your organization.
