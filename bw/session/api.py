from sqlalchemy.orm import select

from bw.state import State
from bw.error import RefreshFailed, NoSuchSession, CannotLogin
from bw.models.session import Session
from bw.environment import ENVIRONMENT
from bw.session.oauth import OAuthSession, BwSession
from bw.endpoints import Root
import aiohttp
import datetime


class SessionApi:
    async def start_oauth_session(self, state: State, discord_id: int, access_code: str) -> OAuthSession:
        data = {
            'grant_type': 'authorization_code',
            'code': access_code,
            'redirect_uri': ENVIRONMENT.discord_oauth_redirect_uri()
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        auth = aiohttp.BasicAuth(ENVIRONMENT.discord_client_id(), ENVIRONMENT.discord_client_secret())
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f'{ENVIRONMENT.discord_api_url()}/oauth2/token', data=data, auth=auth) as response:
                try:
                    response.raise_for_status()
                except aiohttp.ClientResponseError:
                    raise CannotLogin()
                
                access_token_response = await response.json()
        
        oauth_session = OAuthSession(
            access_token=access_token_response['access_token'],
            refresh_token=access_token_response['refresh_token'],
            expire_time=datetime.datetime.now() + datetime.timedelta(seconds=float(access_token_response['expires_in']))
        )
        bw_session = await self.login_to_backend(state, oauth_session)
        
        with state.Session.begin() as session:
            new_session = Session(
                discord_id = discord_id,
                session_token = bw_session.token,
                session_expire = bw_session.expire_time,
                oauth_token = oauth_session.access_token,
                oauth_refresh_token = oauth_session.refresh_token,
                expires_seconds = int(access_token_response['expires_in'])
            )
            session.add(new_session)
            session.commit()
        
        return oauth_session

    async def refresh_oauth_session(self, state: State, oauth_session: OAuthSession) -> OAuthSession:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': oauth_session.refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        auth = aiohttp.BasicAuth(ENVIRONMENT.discord_client_id(), ENVIRONMENT.discord_client_secret())
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f'{ENVIRONMENT.discord_api_url()}/oauth2/token', data=data, auth=auth) as response:
                try:
                    response.raise_for_status()
                except aiohttp.ClientResponseError:
                    raise RefreshFailed()
                
                access_token = await response.json()
        
        with state.Session.begin() as session:
            query = (
                select(Session)
                .values(refresh_token=oauth_session.refresh_token)
            )
            existing_session: Session = session.scalar(query)
            existing_session.token = access_token['access_token']
            existing_session.refresh_token = access_token['refresh_token']
            existing_session.expires_seconds = access_token['expires_in']
            existing_session.session_start = datetime.datetime.now()
            session.commit()
        
        return OAuthSession(
            access_token=access_token['access_token'],
            refresh_token=access_token['refresh_token'],
            expire_time=datetime.datetime.now() + datetime.timedelta(seconds=access_token['expires_in'])
        )
    
    async def login_to_backend(self, state: State, oauth_session: OAuthSession) -> BwSession:
        Root.api.v1.auth.login.discord.get()        
    
    def get_bw_session_from_discord_id(self, state: State, discord_id: int) -> BwSession:
        with state.Session.begin() as session:
            query = (
                select(Session)
                .values(discord_id=discord_id)
            )
            existing_session = session.scalar(query)
            if existing_session is None:
                return BwSession.null()
            return BwSession.from_session(existing_session)

    def get_discord_session_from_discord_id(self, state: State, discord_id: int) -> OAuthSession:
        with state.Session.begin() as session:
            query = (
                select(Session)
                .values(discord_id=discord_id)
            )
            existing_session = session.scalar(query)
            if existing_session is None:
                raise NoSuchSession()
            return OAuthSession.from_session(existing_session)
                

                
