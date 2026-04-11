from bw.interface import User
from discord import ForumChannel
from bw.discord.types import ForumId
from discord import Client
from sqlalchemy import select
from uuid import UUID

from bw.models.discord import MissionForum
from bw.state import State

class DiscordApi:
    async def create_forum_thread(self, channel: ForumChannel, thread_name: str) -> ForumId:
        forum, _ = await channel.create_thread(
            name=thread_name
        )
        return ForumId(forum.id)

    async def get_or_create_mission_thread(self, state: State, channel: ForumChannel, mission_uuid: UUID) -> MissionForum:
        with state.Session.begin() as session:
            query = select(MissionForum).where(MissionForum.mission_uuid == mission_uuid)
            forum = session.scalar(query)
            if forum:
                session.expunge_all()
                return forum
            
            iteration_information = User(state.api_client).iteration_information(iteration_uuid)

            forum_id = await self.create_forum_thread(channel, mission_name)
            forum = MissionForum(mission_uuid=mission_uuid)

            return forum