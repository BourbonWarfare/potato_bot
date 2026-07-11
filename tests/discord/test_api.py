# ruff: noqa: F401, F811

import pytest
from sqlalchemy import select

from bw.discord.api import DiscordApi
from bw.models.discord import MissionForum
from tests.fixtures.discord_objects import (
    FakeForumChannel,
    FakeForumTag,
    fake_forum_channel,
)
from tests.fixtures.responses import (
    SAMPLE_MISSION_UUID,
    sample_mission,
    sample_iteration,
    sample_mission_type,
)
from tests.fixtures.state import in_memory_state


@pytest.mark.asyncio
async def test__discord_api__get_or_create_mission_thread__creates_thread_when_missing(
    in_memory_state, fake_forum_channel, sample_iteration
):
    result = await DiscordApi().get_or_create_mission_thread(in_memory_state, fake_forum_channel, sample_iteration)

    assert len(fake_forum_channel.create_thread_calls) == 1
    assert result.thread_id == 999
    assert result.mission_uuid == SAMPLE_MISSION_UUID


@pytest.mark.asyncio
async def test__discord_api__get_or_create_mission_thread__persists_row(in_memory_state, fake_forum_channel, sample_iteration):
    await DiscordApi().get_or_create_mission_thread(in_memory_state, fake_forum_channel, sample_iteration)

    with in_memory_state.Session() as session:
        rows = session.execute(select(MissionForum)).scalars().all()

    assert len(rows) == 1
    assert rows[0].mission_uuid == SAMPLE_MISSION_UUID
    assert rows[0].thread_id == 999


@pytest.mark.asyncio
async def test__discord_api__get_or_create_mission_thread__returns_existing_row_when_present(
    in_memory_state, fake_forum_channel, sample_iteration
):
    with in_memory_state.Session.begin() as session:
        session.add(MissionForum(mission_uuid=SAMPLE_MISSION_UUID, thread_id=42))

    result = await DiscordApi().get_or_create_mission_thread(in_memory_state, fake_forum_channel, sample_iteration)

    assert result.thread_id == 42
    assert fake_forum_channel.create_thread_calls == []


@pytest.mark.asyncio
async def test__discord_api__get_or_create_mission_thread__applies_matching_tag(
    in_memory_state, fake_forum_channel, sample_iteration
):
    await DiscordApi().get_or_create_mission_thread(in_memory_state, fake_forum_channel, sample_iteration)

    applied = fake_forum_channel.create_thread_calls[0]['applied_tags']
    assert len(applied) == 1
    assert applied[0].name == sample_iteration.mission.mission_type.name


@pytest.mark.asyncio
async def test__discord_api__get_or_create_mission_thread__no_matching_tag_passes_empty_tags(in_memory_state, sample_iteration):
    channel = FakeForumChannel(available_tags=[FakeForumTag(name='WAT', id=7)], new_thread_id=999)

    await DiscordApi().get_or_create_mission_thread(in_memory_state, channel, sample_iteration)

    assert channel.create_thread_calls[0]['applied_tags'] == []


@pytest.mark.asyncio
async def test__discord_api__get_or_create_mission_thread__create_thread_called_with_mission_title(
    in_memory_state, fake_forum_channel, sample_iteration
):
    await DiscordApi().get_or_create_mission_thread(in_memory_state, fake_forum_channel, sample_iteration)

    call = fake_forum_channel.create_thread_calls[0]
    assert call['name'] == sample_iteration.mission.title + '.' + sample_iteration.mission.map
    assert call['embeds'] is not None
    assert len(call['embeds']) == 2  # mission embed + mission type embed
