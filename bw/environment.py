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
                return type_converter(func(entry))
            except ConfigurationKeyNotPresent as e:
                logger.error(f'Configuration entry "{entry}" not present in configuration.')
                raise e
            except ValueError as e:
                logger.error(f'Configuration entry "{entry}" is not of type {type_converter.__name__}.')
                raise e

        return wrapper

    return decorator


class Environment:
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
    def recruitment_channel(self, key: str) -> str:
        return GC[key]

    @config_fetch('backend_address', str, require=False)
    def backend_address(self, key: str) -> str:
        return GC.get(key, 'localhost')

    @config_fetch('backend_port', int)
    def backend_port(self, key: str) -> str:
        return GC[key]

    @config_fetch('backend_token', str)
    def backend_token(self, key: str) -> str:
        return GC[key]

    def local_session_time(self) -> datetime.timedelta:
        return datetime.timedelta(hours=GC.get('local_session_time', 12 + 7))

    def embed_colour_member(self) -> discord.Color:
        return discord.Color.from_str('0xdb1414')

    def embed_colour_staff(self) -> discord.Color:
        return discord.Color.blue()


class Local(Environment):
    pass


class Test(Environment):
    pass


class Production(Environment):
    pass


if GC.get('environment', 'local') == 'prod':
    ENVIRONMENT = Production()
elif GC.get('environment', 'local') == 'test':
    ENVIRONMENT = Test()
else:
    ENVIRONMENT = Local()
