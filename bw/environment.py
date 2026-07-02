import discord
import logging
import datetime
from collections.abc import Callable
from functools import wraps
from typing import Any
from bw.settings import GLOBAL_CONFIGURATION as GC
from bw.error import ConfigurationKeyNotPresent

logger = logging.getLogger('bw')


def config_fetch(entry: str, type_converter: type = str, require: bool = True) -> Callable:
    def decorator(func: Callable[[str], str]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                if require:
                    GC.require(entry)
                return type_converter(func(*args, **kwargs, key=entry))
            except ConfigurationKeyNotPresent as e:
                logger.error(f'Configuration entry "{entry}" not present in configuration.')
                raise e
            except ValueError as e:
                logger.error(f'Configuration entry "{entry}" is not of type {type_converter.__name__}.')
                raise e

        return wrapper

    return decorator


class Environment:
    @config_fetch('backend_secret')
    def backend_bot_token(self, key: str) -> str:
        return GC[key]

    @config_fetch('discord_token')
    def discord_token(self, key: str) -> str:
        return GC[key]

    @config_fetch('orientation_role_id', int)
    def orientor_role(self, key: str) -> str:
        return GC[key]

    @config_fetch('awaiting_orientation_role_id', int)
    def awaiting_orientation_role(self, key: str) -> str:
        return GC[key]

    @config_fetch('recruit_role_id', int)
    def recruit_role(self, key: str) -> str:
        return GC[key]

    @config_fetch('recruitment_channel_id', int)
    def recruitment_channel(self, key: str) -> int:
        return GC[key]

    @config_fetch('mission_forum_id', int)
    def mission_forum_id(self, key: str) -> int:
        return GC[key]

    @config_fetch('arma_channel_id', int)
    def arma_channel_id(self, key: str) -> int:
        return GC[key]

    @config_fetch('tech_channel_id', int)
    def tech_channel_id(self, key: str) -> int:
        return GC[key]

    @config_fetch('backend_address', str, require=False)
    def backend_address(self, key: str) -> str:
        return GC.get(key, 'localhost')

    @config_fetch('backend_port', int)
    def backend_port(self, key: str) -> str:
        return GC[key]

    @config_fetch('discord_client_id', str)
    def discord_client_id(self, key: str) -> str:
        return GC[key]

    @config_fetch('discord_client_secret', str)
    def discord_client_secret(self, key: str) -> str:
        return GC[key]

    @config_fetch('discord_api_url', str)
    def discord_api_url(self, key: str) -> str:
        return GC[key].strip('/')

    def discord_oauth_redirect_uri(self) -> str:
        raise NotImplementedError()

    def db_connection(self) -> str:
        db_driver = GC.require('db_driver').get()
        assert isinstance(db_driver, str)
        if db_driver.split('+')[0] == 'sqlite':
            db_filepath = GC.require('db_filepath').get()
            return f'{db_driver}:///{db_filepath}'
        else:
            db_username, db_password, db_address = GC.require('db_username', 'db_password', 'db_address').get()
            return f'{db_driver}://{db_username}:{db_password}@{db_address}'

    def local_session_time(self) -> datetime.timedelta:
        return datetime.timedelta(hours=GC.get('local_session_time', 12 + 7))

    def embed_colour_member(self) -> discord.Color:
        return discord.Color.from_str('0xdb1414')

    def embed_colour_staff(self) -> discord.Color:
        return discord.Color.blue()

    def db_echo(self) -> bool:
        raise NotImplementedError()


class Local(Environment):
    def db_echo(self) -> bool:
        return True


class Test(Environment):
    def db_echo(self) -> bool:
        return False

    def discord_oauth_redirect_uri(self):
        return 'https://staging.bourbonwarfare.com/auth/login/discord'


class Production(Environment):
    def db_echo(self) -> bool:
        return False

    def discord_oauth_redirect_uri(self):
        return 'https://bourbonwarfare.com/auth/login/discord'


if GC.get('environment', 'local') == 'prod':
    logger.info('Using production environment')
    ENVIRONMENT = Production()
elif GC.get('environment', 'local') == 'test':
    logger.info('Using staging envrioment')
    ENVIRONMENT = Test()
else:
    logger.info('Using local envrioment')
    ENVIRONMENT = Local()
