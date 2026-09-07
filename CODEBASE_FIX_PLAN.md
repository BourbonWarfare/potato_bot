# Codebase Fix Plan

Branch: `audit/fix-plan`

This is a review/plan only. No behavior fixes should be implemented until approved.

## Current health check

Commands run during audit:

- `uv run pytest` → **1 failure, 83 passing**
- `uv run ruff check` → **6 lint errors**
- `uv run ty check` → **46 type diagnostics**
- `rg "create_webhook|webhook" ...` → channel-created webhook usage is centralized in `bw/commands/webhooks.py`; other references are Discord interaction followups/type hints.

## Priority 0: keep webhook cleanup safe

The manual channel webhook creation appears fixed, but I would add tests so it cannot regress.

Planned work:

1. Add tests for `temporary_webhook`:
   - creates a webhook for `discord.TextChannel`-like objects;
   - deletes the webhook when the context exits normally;
   - deletes the webhook when the context exits through an exception;
   - yields a `discord.Thread` directly without trying to create/delete a webhook;
   - logs but does not mask the original error if delete fails.
2. Add a lightweight grep-style test or lint guard to fail if `.create_webhook(` appears outside `bw/commands/webhooks.py`.

## Priority 1: fix currently failing tests and obvious behavior bugs

### 1. Mission thread lookup test/API mismatch

Current failure:

- `tests/commands/test_mission_making.py::test__mission_event_handler__uploaded__delegates_thread_lookup_to_discord_api`

The test expects `DiscordApi.get_or_create_mission_thread(..., mission_information)`, but the implementation now passes full `iteration_information` because thread naming uses `iteration_information.filename`.

Planned options:

- Preferred: update the test to assert the full iteration object is passed, and add/confirm coverage in `tests/discord/test_api.py` that `DiscordApi` uses `iteration_information.mission` for DB lookup and `iteration_information.filename` for thread title.
- Alternative: split `DiscordApi.get_or_create_mission_thread` signature into explicit `mission_information` plus optional `filename`, but this is probably less clean.

### 2. Backend address is ignored

`bw/interface.py::server_url` currently hardcodes `localhost` and ignores `ENVIRONMENT.backend_address()`.

Planned fix:

```py
address = ENVIRONMENT.backend_address()
port = ENVIRONMENT.backend_port()
```

Add unit coverage so configured backend host is used.

### 3. Session refresh does not reliably retry/update headers

Pattern in `bw/interface.py`:

```py
async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
    async with self.client.backend_session(session=session):
        ...
```

This creates the aiohttp session before `backend_session()` may refresh credentials, so requests can use stale headers. Also, `UserClient.backend_session()` catches a 401, refreshes, and suppresses the exception without retrying the failed HTTP request, which can make callers return `None` or fail later.

Planned refactor:

1. Move request execution into a small authenticated request helper.
2. Ensure token refresh happens before headers are attached.
3. On 401, refresh once and retry the original request once.
4. Keep backend/Discord connectivity errors translated to domain errors.
5. Add tests for expired token pre-refresh and 401 retry.

## Priority 2: reduce duplicated command error handling

Several commands repeat the same flow:

- `await interaction.response.defer()`
- `get_session(interaction.followup, interaction.user)`
- catch `CannotReachBwBackend`
- catch `CannotReachDiscord`
- construct `User(UserClient(...))`

Seen in:

- `bw/commands/staff.py`
- `bw/commands/modals/staff.py`
- `bw/commands/modals/mission_making.py`
- `bw/commands/community.py`

Planned refactor:

1. Add a helper/context manager, likely in `bw/commands/utils.py`, such as:

```py
async def get_user_interface(interaction) -> User | None:
    ...
```

or

```py
async with user_interface_for(interaction) as interface:
    ...
```

2. Centralize backend/Discord failure responses.
3. Keep modal/thread-specific response destinations configurable.
4. Refactor staff commands first because they have the most duplication.

## Priority 3: type-safety and Discord object validation

`ty check` reports many real risks around `bot.get_channel(...)`, `interaction.guild`, and `interaction.user` being broader unions than the code assumes.

Planned work:

1. Add small typed helpers:
   - `require_text_channel(bot, channel_id, name)`
   - `require_forum_channel(bot, channel_id, name)`
   - `require_member(interaction)`
   - `require_guild(interaction)`
   - `require_role(guild, role_id, name)`
2. Replace raw `assert isinstance(...)` where runtime failure should produce a clear log/error.
3. Use these helpers in:
   - `bw/commands/community.py`
   - `bw/commands/recruitment.py`
   - `bw/commands/staff.py`
   - `bw/commands/mission_making.py`
4. Broaden embed function user parameters from `discord.User` to `discord.abc.User` or `discord.User | discord.Member` where appropriate.

## Priority 4: clean up lint failures

Current `ruff check` failures:

1. Unused `VoiceChannel` import in `bw/commands/community.py`.
2. Star imports in `bw/error/__init__.py`.

Planned fix:

- Remove the unused import.
- Replace `from bw.error.foo import *` with explicit re-exports and `__all__`.

## Priority 5: simplify Staff command server operations

`bw/commands/staff.py` contains repeated status/update/start/stop/restart handling, plus repeated aiohttp status mapping.

Planned refactor:

1. Create shared mapping from backend HTTP errors to embeds.
2. Create shared ARMA server operation helper:

```py
async def run_server_operation(interaction, server, operation, call): ...
```

3. Avoid using possibly undefined `response` in exception branches of `get_server_status`.
4. Normalize enum usage: functions should accept `ArmaCommand`/`UpdateChoices`, not loose `str` after conversion.
5. Add focused unit tests for 401/403/404/500/unexpected cases.

## Priority 6: make SSE/event broker more robust

`bw/events/broker.py` works, but can be hardened.

Planned improvements:

1. Parse SSE lines defensively; ignore/comment lines without `:` instead of crashing.
2. Log handler exceptions with `logger.exception(...)` instead of separate error + debug traceback.
3. Consider publishing handlers concurrently only if ordering is not important.
4. Review `tasks.loop(seconds=15)` containing an internal `while True`; simplify to either a single reconnect loop task or a true periodic loop, not both.
5. Add tests for malformed SSE lines and backend reconnect behavior.

## Priority 7: configuration cleanup

Issues found:

- `ConfigContext.get()` says it returns `str | tuple[str, ...]`, but `dict.get()` can return `None`.
- `Environment` methods often declare `str` but decorators convert to `int`.
- `config_fetch` decorator typing confuses ty.
- Typos in log messages: `envrioment`, `attemptign`, `occured`.

Planned work:

1. Make `Configuration.require(...).get()` return non-optional values by using `self._config[key]` after require.
2. Correct environment method annotations to match converted return types.
3. Type `config_fetch` using `ParamSpec`/`TypeVar` or keep it simple but accurate.
4. Fix typo-only changes separately.

## Priority 8: mission upload modal cleanup/simplification

Potential improvements in `bw/commands/modals/mission_making.py`:

1. Initialize `server` defensively before scanning children; avoid relying on later `assert isinstance(server, ui.Select)` if selector was not found.
2. Return after potential issues length error, matching the description length branch.
3. Extract upload error-to-human-message handling into a function with tests.
4. Ensure temporary directories/files used by forced upload are cleaned up after success/failure, not only view timeout.

## Priority 9: tests for the refactors

After each batch:

- `uv run ruff check`
- `uv run pytest`
- `uv run ty check`
- `python -m compileall bw`

Target final state:

- tests pass;
- ruff passes;
- ty either passes or has a documented, intentionally ignored set of diagnostics;
- no manual channel webhook creation outside the temporary webhook manager.

## Suggested implementation order

1. Add webhook manager regression tests.
2. Fix the current failing test/API expectation.
3. Fix `server_url()` backend address.
4. Refactor authenticated backend request/session refresh handling.
5. Add typed Discord lookup helpers and apply to community/recruitment/staff.
6. Clean ruff failures.
7. Simplify staff command duplication.
8. Harden SSE broker.
9. Clean mission upload modal edge cases.
