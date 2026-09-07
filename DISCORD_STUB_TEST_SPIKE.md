# Discord Stub Integration Test Spike

Goal: add integration-ish tests for Discord command/event behavior without using the real Discord API.

## Recommendation

Use a small project-owned fake Discord layer instead of a broad third-party Discord test harness.

The bot mostly needs to verify observable behavior:

- a response was deferred;
- a response/followup was sent;
- a modal was sent;
- a channel/thread received a message;
- a thread was created;
- a role was added;
- a reaction was added;
- a channel was edited;
- backend/session helpers were called on edge cases.

We do **not** need to emulate Discord transport, slash-command registration, gateway events, permissions, or rendering.

## Existing starting point

There is already a useful base in:

```txt
tests/fixtures/discord_objects.py
```

It currently includes:

- `FakeBot`
- `FakeForumChannel`
- `FakeForumTag`
- `FakeMessage`
- `FakeThread`

This should be expanded instead of replaced.

## Minimal fake API needed

Add only what current tests need. Keep every fake simple and call-recording focused.

### FakeInteraction

Suggested attributes:

```py
class FakeInteraction:
    user: FakeUser | FakeMember
    guild: FakeGuild | None
    channel: FakeTextChannel | FakeThread | None
    response: FakeInteractionResponse
    followup: FakeFollowup

    async def edit_original_response(...): ...
```

Records:

- original response edits
- user/guild/channel available to command code

### FakeInteractionResponse

Methods:

```py
async def defer(*, ephemeral=False, thinking=False): ...
async def send_message(content=None, *, embed=None, embeds=None, ephemeral=False, file=None, view=None): ...
async def send_modal(modal): ...
```

Records:

- `deferred: bool`
- `defer_kwargs`
- `sent_messages: list[FakeMessage]`
- `sent_modal`

For message responses that need thread creation, return a small object whose `.resource` is a `FakeInteractionMessage`.

### FakeFollowup

Methods:

```py
async def send(content=None, *, embed=None, embeds=None, ephemeral=False, file=None, view=None): ...
```

Records:

- `sent: list[FakeMessage]`

### FakeUser / FakeMember

`FakeUser`:

```py
id: int
mention: str
global_name: str | None
```

`FakeMember(FakeUser)`:

```py
nick: str | None
roles: list[FakeRole]
added_roles: list[FakeRole]

def get_role(role_id): ...
async def add_roles(*roles, reason=None): ...
```

Records:

- roles added
- add-role reasons

### FakeGuild

Methods:

```py
def get_role(role_id): ...
```

Records/config:

- roles by id

### FakeRole

Attributes:

```py
id: int
mention: str
name: str
```

### FakeTextChannel

Methods:

```py
async def send(content=None, *, embed=None, embeds=None, file=None, view=None): ...
async def create_webhook(name, reason=None): ...
async def fetch_message(message_id): ...
async def edit(**kwargs): ...
```

Records:

- sent messages
- created webhooks
- fetched message IDs
- edits

### FakeVoiceChannel

For RDP monitor tests:

```py
async def send(...): ...
async def edit(name=None, reason=None): ...
```

Records:

- sent messages
- edits

### FakeInteractionMessage / FakeMessage

`FakeMessage` already exists but may need:

```py
id: int
content: str | None
embed: Any
embeds: list[Any]
file: Any
view: Any
reactions: list[FakeReaction]

async def add_reaction(emoji): ...
async def create_thread(name): ...
```

Records:

- added reactions
- created thread

### FakeReaction

Needed for mission-end notification tests:

```py
async def users():
    yield fake_user
```

### FakeAttachment

For mission upload modal tests:

```py
filename: str
async def save(file): ...
```

Records:

- saved target received data

## Patching strategy

Some production code uses `isinstance(..., discord.TextChannel)` or similar. For fake tests, there are two possible approaches.

### Preferred short-term approach

Patch the imported Discord classes in the module under test:

```py
mocker.patch('bw.commands.recruitment.discord.Member', FakeMember)
mocker.patch('bw.commands.discord_utils.discord.TextChannel', FakeTextChannel)
```

This mirrors the existing pattern in mission-making tests:

```py
mocker.patch('bw.commands.mission_making.ForumChannel', FakeForumChannel)
mocker.patch('bw.commands.mission_making.Thread', FakeThread)
```

### Longer-term improvement

Move most `isinstance` checks behind helpers in `bw/commands/discord_utils.py`, then tests only need to patch/check the helper behavior once.

## Test style rules

Keep tests stable by checking observable behavior, not exact strings or implementation details.

Good assertions:

```py
assert interaction.response.deferred is True
assert len(channel.sent) == 1
assert member.added_roles == [awaiting_role]
assert interaction.response.sent_modal is not None
assert channel.edits
assert backend_method.assert_awaited_once()
```

Avoid assertions like:

```py
assert channel.sent[0].content == 'exact human-facing message'
assert embed.title == 'exact title'
assert helper_was_called_only_because_current_implementation_uses_helper
```

String checks should only be used when the string is itself the logic boundary, such as endpoint path construction or protocol-level values. For Discord-rendered output, prefer “something was posted” and edge-case side effects.

## Best first tests to add

### 1. Recruitment orientation command

Observable behaviors:

- Recruit user receives a non-ephemeral orientation response.
- Recruit without awaiting-orientation role gets that role added.
- Recruitment channel receives one message.
- Recruit already awaiting orientation does not get duplicate role added.
- Non-recruit receives a response and no channel message is posted.

Required fakes:

- `FakeInteraction`
- `FakeInteractionResponse`
- `FakeMember`
- `FakeGuild`
- `FakeRole`
- `FakeTextChannel`
- `FakeBot`

### 2. Staff event handlers

Observable behaviors:

- ARMA server events post to command channel.
- Cron run event posts to cron channel.
- RDP disconnect posts and edits RDP channel.
- RDP authentication success posts and edits RDP channel.
- Unknown/unhandled event does nothing.

Required fakes:

- `FakeBot`
- `FakeTextChannel`
- `FakeVoiceChannel`
- event fixtures already exist under `tests/fixtures/events.py` or can be added.

### 3. Session failure helper

Observable behaviors:

- Backend reachability error sends one followup.
- Discord reachability error sends one followup.
- Both are ephemeral.

Required fakes:

- `FakeInteraction`
- `FakeFollowup`

### 4. Mission upload modal edge cases

Observable behaviors:

- Missing server selector responds with an error and does not upload.
- Too-long description posts to thread and returns before upload.
- Too-long potential issues posts to thread and returns before upload.
- Backend validation error posts a force-upload view only for force-allowed errors.

Required fakes:

- `FakeInteraction`
- `FakeInteractionResponse`
- `FakeFollowup`
- `FakeThread`
- `FakeTextChannel`
- `FakeInteractionMessage`
- `FakeAttachment`

This is the highest-value but most annoying batch because `discord.ui` components are involved.

## Third-party library note

`dpytest` may be the existing library worth considering, but I would not add it initially.

Reasons:

- this bot is slash-command/modal heavy;
- we mostly need side-effect assertions, not Discord protocol simulation;
- direct fakes will be smaller and easier to reason about;
- adding a broad Discord testing library can make tests slower and more coupled to Discord internals.

Revisit `dpytest` only if we later want to test command dispatch/registration behavior instead of directly calling command callbacks/modal methods.

## Implementation plan

1. Expand `tests/fixtures/discord_objects.py` with fake interactions, responses, followups, guilds, roles, users/members, text/voice channels, and attachments.
2. Add recruitment orientation tests first.
3. Add staff event-handler tests second.
4. Add session failure helper tests third.
5. Add mission upload modal edge-case tests last.
6. Keep fakes intentionally incomplete; add behavior only when a test needs it.
7. Run after each batch:

```sh
uv run ruff check
uv run ty check
uv run pytest
```

## Estimated effort

- Base fake layer: 1-2 hours.
- Recruitment tests: 30-60 minutes.
- Staff event tests: 30-60 minutes.
- Session failure helper tests: 15-30 minutes.
- Mission upload modal edge cases: 1-3 hours depending on how much `discord.ui` needs to be patched or avoided.

Overall: roughly half a day for useful coverage, maybe a full day if we go deep on modal/file-upload paths.
