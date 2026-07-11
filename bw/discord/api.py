import re
import bw.embeds
from bw.missions.response import IterationInformationResponse, MissionInformationResponse
from discord import ForumChannel, ForumTag
from bw.discord.types import ForumId
from sqlalchemy import select

from bw.models.discord import MissionForum
from bw.state import State


class DiscordApi:
    async def does_mission_thread_exist(self, state: State, mission_information: MissionInformationResponse) -> bool:
        with state.Session.begin() as session:
            query = select(MissionForum).where(MissionForum.mission_uuid == mission_information.uuid)
            forum = session.scalar(query)
            return bool(forum)

    async def get_or_create_mission_thread(
        self, state: State, channel: ForumChannel, iteration_information: IterationInformationResponse
    ) -> MissionForum:
        mission_information = iteration_information.mission
        with state.Session.begin() as session:
            query = select(MissionForum).where(MissionForum.mission_uuid == mission_information.uuid)
            forum = session.scalar(query)
            if not forum:
                default_tags: list[ForumTag] = []
                for available_tag in channel.available_tags:
                    if available_tag.name == mission_information.mission_type.name:
                        default_tags.append(available_tag)

                    if available_tag.name == 'Needs Testing':
                        default_tags.append(available_tag)

                mission_file_no_version = re.sub('_[vV][0-9]+', '', iteration_information.filename)
                discord_forum, _ = await channel.create_thread(
                    name=mission_file_no_version,
                    embeds=bw.embeds.mission_information(mission_information),
                    reason='Automated mission thread creation',
                    applied_tags=default_tags,
                )
                forum_id = ForumId(discord_forum.id)
                forum = MissionForum(mission_uuid=mission_information.uuid, thread_id=forum_id)

                session.add(forum)
                session.flush()

            session.expunge(forum)
        return forum
