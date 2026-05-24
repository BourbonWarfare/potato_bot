# potato_bot

The Discord bot for the [Bourbon Warfare](https://bourbonwarfare.com) ARMA group.

It is the user-facing half of a pair. The backend is [potato_db](https://github.com/bourbonwarfare/potato_db), which holds the data and exposes the API; this bot is a thin Discord frontend that talks to it over HTTP.

## What it does

- **Recruitment & orientation.** Tracks recruits and orientors, manages role assignments, and gates the recruitment workflow inside Discord.
- **Mission making.** Lets mission makers upload `.pbo` files through Discord, forwards them to the backend, and reports back iteration/version info from the mission database.
- **ARMA server ops.** Wraps the backend's server-ops endpoints in Discord commands so authorised users can start, stop, restart, update, and mod-update ARMA servers from chat.
- **Staff tooling.** Admin commands for staff that wrap the backend's privileged endpoints.
- **Community helpers.** Miscellaneous quality-of-life slash commands.
- **Authentication.** Brokers Discord OAuth2 between users and the backend, refreshing sessions transparently.

Every command is implemented as a `discord.py` cog under [`bw/commands/`](./bw/commands).

## Technology

- **Python 3.12**, dependencies pinned with [uv](https://docs.astral.sh/uv/).
- **[discord.py](https://discordpy.readthedocs.io/)** for the Discord gateway and slash commands.
- **[aiohttp](https://docs.aiohttp.org/)** + **aiodns** for talking to the backend.
- **[SQLAlchemy](https://www.sqlalchemy.org/)** + **[Alembic](https://alembic.sqlalchemy.org/)** against **SQLite** for bot-local state (sessions, caches, OAuth bookkeeping).
- **[beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)** for parsing HTML the bot scrapes for some helper commands.
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** for configuration via `settings.env`.
- **[pytest](https://pytest.org/)** (+ `pytest-asyncio`, `pytest-mock`, `pytest-cov`) for tests, **[ruff](https://docs.astral.sh/ruff/)** for lint and format, **[ty](https://github.com/astral-sh/ty)** for type checking.

## Architecture

The bot is outbound-only. It connects to:

1. **Discord**, via the discord.py gateway.
2. **The potato_db backend**, via HTTP (`bw/interface.py`). Paths are resolved through the typed builder in `bw/endpoints/`, so endpoint changes on the backend surface here as compile-time-ish errors instead of stringly-typed runtime failures.

There is no inbound HTTP server. The bot does not need any ports open.

The bot authenticates to the backend in two ways:

- **Bot token (`backend_secret`).** A long-lived shared secret matched against a "bot user" on the backend. Used for actions the bot performs on its own behalf — periodic health checks, fetches, etc.
- **User OAuth2 sessions.** When a Discord user runs a command that touches their own data on the backend (a mission upload, a staff action), the bot relays their Discord OAuth tokens to the backend to mint a per-user session.

## Building and running

See [BUILDING.md](./BUILDING.md) for local setup, tests, migrations, and the production runbook.

## License

See [LICENSE](./LICENSE).
