# ruff: noqa: F401, F811

from unittest.mock import ANY

import pytest

from bw.commands.mission_making import MissionMaking
from bw.error import MisconfiguredForumChannel
from tests.fixtures.discord_objects import FakeBot, FakeForumChannel, FakeThread
from tests.fixtures.events import (
    cosigned_event,
    reviewed_event,
    unknown_event,
    uploaded_event,
)
from tests.fixtures.responses import sample_iteration, sample_mission, sample_mission_type


FORUM_CHANNEL_ID = 12345
THREAD_ID = 999


@pytest.fixture
def patched_env(mocker):
    from bw.environment import ENVIRONMENT

    mocker.patch.object(ENVIRONMENT, 'mission_forum_id', return_value=FORUM_CHANNEL_ID)


@pytest.fixture
def patched_globals(mocker):
    """Stop MissionMaking.__init__ from registering against the real global broker,
    and rebind isinstance() targets so our fakes are accepted in place of discord types."""
    mocker.patch('bw.commands.mission_making.global_event_broker')
    mocker.patch('bw.commands.mission_making.State')
    mocker.patch('bw.commands.mission_making.ForumChannel', FakeForumChannel)
    mocker.patch('bw.commands.mission_making.Thread', FakeThread)


@pytest.fixture
def mock_user(mocker, sample_iteration):
    user_class = mocker.patch('bw.commands.mission_making.User')
    user_instance = user_class.return_value
    user_instance.iteration_information = mocker.AsyncMock(return_value=sample_iteration)
    return user_instance


@pytest.fixture
def mock_discord_api(mocker):
    api_class = mocker.patch('bw.commands.mission_making.DiscordApi')
    api_instance = api_class.return_value
    forum_row = mocker.MagicMock()
    forum_row.thread_id = THREAD_ID
    api_instance.get_or_create_mission_thread = mocker.AsyncMock(return_value=forum_row)
    return api_instance


@pytest.fixture
def forum_thread():
    return FakeThread(id=THREAD_ID)


@pytest.fixture
def cog(patched_env, patched_globals, mock_user, mock_discord_api, forum_thread):
    forum_channel = FakeForumChannel()
    bot = FakeBot(channels={FORUM_CHANNEL_ID: forum_channel, THREAD_ID: forum_thread})
    return MissionMaking(bot)


@pytest.mark.asyncio
async def test__mission_event_handler__non_forum_channel_raises_misconfigured(
    patched_env, patched_globals, uploaded_event
):
    bot = FakeBot(channels={FORUM_CHANNEL_ID: 'not-a-forum-channel'})
    cog = MissionMaking(bot)

    with pytest.raises(MisconfiguredForumChannel):
        await cog.mission_event_handler(uploaded_event)


@pytest.mark.asyncio
async def test__mission_event_handler__channel_missing_raises_misconfigured(
    patched_env, patched_globals, uploaded_event
):
    bot = FakeBot(channels={})  # get_channel returns None
    cog = MissionMaking(bot)

    with pytest.raises(MisconfiguredForumChannel):
        await cog.mission_event_handler(uploaded_event)


@pytest.mark.asyncio
async def test__mission_event_handler__uploaded__posts_iteration_embed(
    cog, forum_thread, mock_user, mock_discord_api, uploaded_event
):
    await cog.mission_event_handler(uploaded_event)

    assert len(forum_thread.sent) == 1
    assert forum_thread.sent[0].embed is not None
    assert forum_thread.sent[0].content is None


@pytest.mark.asyncio
async def test__mission_event_handler__uploaded__looks_up_iteration_from_event_data(
    cog, mock_user, uploaded_event
):
    await cog.mission_event_handler(uploaded_event)

    mock_user.iteration_information.assert_awaited_once()
    iteration_uuid = mock_user.iteration_information.call_args.args[0]
    assert str(iteration_uuid) == uploaded_event.data['iteration']


@pytest.mark.asyncio
async def test__mission_event_handler__uploaded__delegates_thread_lookup_to_discord_api(
    cog, mock_discord_api, sample_iteration, uploaded_event
):
    await cog.mission_event_handler(uploaded_event)

    mock_discord_api.get_or_create_mission_thread.assert_awaited_once()
    _, _, mission_arg = mock_discord_api.get_or_create_mission_thread.call_args.args
    assert mission_arg is sample_iteration.mission


@pytest.mark.asyncio
async def test__mission_event_handler__uploaded__thread_lookup_returns_non_thread_raises(
    patched_env, patched_globals, mock_user, mock_discord_api, uploaded_event
):
    bot = FakeBot(channels={FORUM_CHANNEL_ID: FakeForumChannel(), THREAD_ID: 'not-a-thread'})
    cog = MissionMaking(bot)

    with pytest.raises(MisconfiguredForumChannel):
        await cog.mission_event_handler(uploaded_event)


@pytest.mark.asyncio
async def test__mission_event_handler__reviewed__posts_review_notice(
    cog, forum_thread, mock_user, reviewed_event, sample_iteration
):
    await cog.mission_event_handler(reviewed_event)

    assert len(forum_thread.sent) == 1
    message = forum_thread.sent[0]
    assert message.content is not None
    assert str(sample_iteration.iteration) in message.content
    assert message.embed is None


@pytest.mark.asyncio
async def test__mission_event_handler__cosigned__is_skipped(
    cog, forum_thread, mock_user, mock_discord_api, cosigned_event
):
    await cog.mission_event_handler(cosigned_event)

    assert forum_thread.sent == []
    mock_user.iteration_information.assert_not_awaited()
    mock_discord_api.get_or_create_mission_thread.assert_not_awaited()


@pytest.mark.asyncio
async def test__mission_event_handler__unknown_event__is_skipped(
    cog, forum_thread, mock_user, mock_discord_api, unknown_event
):
    await cog.mission_event_handler(unknown_event)

    assert forum_thread.sent == []
    mock_user.iteration_information.assert_not_awaited()
    mock_discord_api.get_or_create_mission_thread.assert_not_awaited()
