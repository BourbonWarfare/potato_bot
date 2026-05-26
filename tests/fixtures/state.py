"""In-memory sqlite State for code that hits bw.state.Session. Only what our DB
access actually needs is wired up."""

from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bw.models import Base
import bw.models.discord  # noqa: F401 — registers MissionForum on Base.metadata


@dataclass
class FakeState:
    Session: sessionmaker


@pytest.fixture
def in_memory_state():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    yield FakeState(Session=sessionmaker(engine))
    engine.dispose()
