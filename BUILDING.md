# Building potato_bot

This guide covers local development, tests, the local SQLite migrations, the cross-repo workflow with `potato_db`, and the production runbook.

## Prerequisites

- **Python 3.12** (the project pins `==3.12.*` in `pyproject.toml`).
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** for dependency and virtualenv management.
- **A registered Discord application** with a bot user. You will need its token, client ID, and client secret.
- **A reachable [potato_db](https://github.com/bourbonwarfare/potato_db) instance.** The bot is useless without one; see the cross-repo notes below.

## Install

```sh
git clone https://github.com/bourbonwarfare/potato_bot.git
cd potato_bot
uv sync --locked --all-extras --dev
```

Available extras:

- `tests` — `pytest` and friends.
- `development` — `ruff`, `ty`, `pre-commit`.
- `prod` — currently empty (production runs from the base dependencies).

Install the pre-commit hooks once:

```sh
uv run pre-commit install
```

## Configure

Configuration lives in `settings.env` at the repo root. It is a normal `.env` file: `KEY=value` lines, `#` comments, blank lines ignored. A working example for local development:

```env
environment=local

# Discord
discord_token=...                       # the bot user's token
discord_client_id=...                   # OAuth client id of the same app
discord_client_secret=...               # OAuth client secret
discord_api_url=https://discord.com/api/v10

# Backend (potato_db)
backend_address=localhost
backend_port=8080
backend_secret=...                      # must match a bot token the backend accepts

# Roles & channels the bot relies on
mission_forum_id=...
orientation_role_id=...
awaiting_orientation_role_id=...
recruit_role_id=...
recruitment_channel_id=...

# Local SQLite store
DB_DRIVER=sqlite
DB_NAME=potbot
DB_FILEPATH=potbot.db

# Optional
local_session_time=19                   # hours; defaults to 19 if unset
```

### Required keys, by feature

- **Discord gateway**: `discord_token`.
- **Discord OAuth**: `discord_client_id`, `discord_client_secret`, `discord_api_url`.
- **Backend calls**: `backend_secret`, `backend_port` (and `backend_address` if not `localhost`).
- **Recruitment / orientation flow**: `mission_forum_id`, `orientation_role_id`, `awaiting_orientation_role_id`, `recruit_role_id`, `recruitment_channel_id`.
- **Database**: `db_driver`, `db_name`, and either `db_filepath` (SQLite) or `db_username` + `db_password` + `db_address` (network DB).

Environment variables override `settings.env` if both define the same key. Secrets belong in the process environment (or systemd `EnvironmentFile=`), not in a committed `settings.env`.

## Database migrations

The bot keeps a small local store (sessions, caches, OAuth bookkeeping) in SQLite. Alembic lives in `alembic/`. Bring it up to head:

```sh
uv run alembic upgrade head
```

Other common commands:

```sh
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic current
uv run alembic history
```

The bot's database is independent from the backend's: bot-local state lives here, **shared domain data** (users, missions, groups) lives in the backend. When a backend migration changes the shape of an API response, the bot's models or response dataclasses may need to follow — but the SQLite schema usually does not.

## Cross-repo workflow

For anything beyond unit tests, you will want both repos running side by side.

1. **Start `potato_db` first.** Follow its [BUILDING.md](https://github.com/bourbonwarfare/potato_db/blob/main/BUILDING.md). For local development that means Postgres up, `conf.kv` filled in, migrations applied, and `uv run python main.py` serving on `http://localhost:8080`.

2. **Point the bot at it.** In `settings.env`:
   ```env
   backend_address=localhost
   backend_port=8080
   ```
   If you are running the backend on another host or port, set them accordingly.

3. **Share the bot token.** The bot authenticates to the backend using `backend_secret` against the backend's `/api/v1/auth/login/bot` endpoint. The value here must match a bot token the backend has been told to accept (the backend uses the same login route for its cron runner via `cron_token` — they are not the same token, but they are the same shape).

4. **Start the bot.**
   ```sh
   uv run python main.py
   ```
   On startup the bot connects to Discord, syncs slash commands if the version changed, and starts its event broker. Backend connectivity is lazy — the first command that needs the backend will trigger a `/api/v1/auth/login/bot` exchange.

## Run locally

```sh
uv run python main.py
```

`main.py` reads `environment` from `settings.env`:

- `local` (or unset) → SQL echo on, OAuth redirect URI is not used.
- `test` → SQL echo off, OAuth redirect URI points at `staging.bourbonwarfare.com`.
- `prod` → SQL echo off, OAuth redirect URI points at `bourbonwarfare.com`.

The bot is a single long-running process. There is no separate worker, no inbound HTTP server, no port to expose.

## Tests

```sh
uv run pytest                  # all tests
uv run pytest --cov=bw         # with coverage
uv run pytest tests/foo.py     # a single file
```

The unit tests do not need a real backend or a real Discord connection; everything network-facing is mocked. CI installs `--extra tests --dev` and runs `pytest --cov=bw`.

## Lint, format, type-check

```sh
uv run ruff check              # lint
uv run ruff format             # format
uv run ty check                # type check
```

The pre-commit hook runs `ruff check` and `ruff format` on staged files.

## Production runbook

Production deployment is one long-running process. There is nothing to expose publicly.

1. **Provision the host.**
   - Install Python 3.12 and uv.
   - Make sure the backend is reachable from this host on `backend_address:backend_port`. If the backend is on the same host, `localhost` is fine and nothing else needs to listen on the network.

2. **Deploy the code.**
   ```sh
   git clone https://github.com/bourbonwarfare/potato_bot.git /opt/potato_bot
   cd /opt/potato_bot
   uv sync --locked
   ```

3. **Write `settings.env`** with `environment=prod`, the production Discord token / client credentials, the production backend address, and the production role/channel IDs.

   Keep `settings.env` out of git. Either deploy it as a separate file owned by the service user, or load secrets via systemd `EnvironmentFile=`.

4. **Apply migrations.**
   ```sh
   uv run alembic upgrade head
   ```

5. **Run the bot under a supervisor.** A minimal systemd unit:

   ```ini
   # /etc/systemd/system/potato-bot.service
   [Unit]
   Description=potato_bot Discord bot
   After=network-online.target potato-db.service
   Wants=network-online.target
   # Hard dependency on the backend if it is on the same host:
   Requires=potato-db.service

   [Service]
   Type=simple
   User=potato
   WorkingDirectory=/opt/potato_bot
   EnvironmentFile=/etc/potato_bot/secrets.env
   ExecStart=/usr/local/bin/uv run python main.py
   Restart=on-failure
   RestartSec=5s

   [Install]
   WantedBy=multi-user.target
   ```

6. **Upgrades.**
   ```sh
   git pull
   uv sync --locked
   uv run alembic upgrade head
   systemctl restart potato-bot
   ```

   The bot detects a version bump (via `bw/version.py` vs. a `version.txt` it writes on startup) and re-syncs the Discord command tree automatically.

## CI

`.github/workflows/test_runner.yml` runs `pytest --cov=bw` with `uv sync --locked --extra tests --dev`. A test `.env` is materialised from the `TEST_CONF` GitHub secret.

`.github/workflows/code_quality.yml` runs the ruff hooks. Match what CI does locally with:

```sh
uv run pre-commit run --all-files
uv run pytest
```
