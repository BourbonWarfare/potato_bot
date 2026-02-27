from sqlalchemy.util import classproperty
import logging
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from bw.environment import ENVIRONMENT
from bw.settings import GLOBAL_CONFIGURATION
from bw.arma_server_cache import ArmaServerCache
from bw.error import StateUsedBeforeDefined

logger = logging.getLogger('bw.state')


class DatabaseConnection:
    def __init__(self, engine):
        self.engine = engine
        self.session_maker = sessionmaker(self.engine)


class State:
    state_: Optional['State'] = None

    def _connection(self) -> str:
        return ENVIRONMENT.db_connection()

    def _setup_engine(self, echo, db_name: str):
        logger.info(f'creating DB engine "{db_name}"')
        return create_engine(f'{self._connection()}', echo=echo)

    def __init__(self):
        if State.state_ is not None:
            return
        self.engine_map = {}
        self.arma_server_cache_ = ArmaServerCache()
        State.state_ = self

        if 'db_name' in GLOBAL_CONFIGURATION:
            self.default_database = GLOBAL_CONFIGURATION['db_name']
            self.register_database(self.default_database, echo=ENVIRONMENT.db_echo())

    def register_database(self, database_name: str, echo=False):
        self.engine_map[database_name] = DatabaseConnection(self._setup_engine(echo=echo, db_name=database_name))

    @property
    def arma_server_cache(self) -> ArmaServerCache:
        return self.arma_server_cache_

    @property
    def default_engine(self) -> DatabaseConnection:
        return self.engine_map[self.default_database]

    @property
    def Engine(self) -> Engine:
        return self.default_engine.engine

    @property
    def Session(self) -> sessionmaker[Session]:
        return self.default_engine.session_maker

    @classproperty
    def state(cls) -> 'State':
        if not cls.state_:
            cls.state_ = State()
        return cls.state_
