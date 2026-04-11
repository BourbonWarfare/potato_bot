import bw.embeds
from bw.missions.response import MissionInformationResponse
from discord import ForumChannel
from bw.discord.types import ForumId
from sqlalchemy import select

from bw.models.discord import MissionForum
from bw.state import State


class DiscordApi:
    async def get_or_create_mission_thread(
        self, state: State, channel: ForumChannel, mission_information: MissionInformationResponse
    ) -> MissionForum:
        with state.Session.begin() as session:
            query = select(MissionForum).where(MissionForum.mission_uuid == mission_information.uuid)
            forum = session.scalar(query)
            if not forum:
                tag = None
                for available_tag in channel.available_tags:
                    if available_tag.name == mission_information.mission_type.name:
                        tag = available_tag
                        break
                discord_forum, _ = await channel.create_thread(
                    name=mission_information.title,
                    embeds=bw.embeds.mission_information(mission_information),
                    reason='Automated mission thread creation',
                    applied_tags=[tag] if tag is not None else [],
                )
                forum_id = ForumId(discord_forum.id)
                forum = MissionForum(mission_uuid=mission_information.uuid, thread_id=forum_id)

                session.add(forum)
                session.flush()

            session.expunge(forum)
        return forum
