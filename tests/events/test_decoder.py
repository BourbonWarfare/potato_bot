# ruff: noqa: F401

import uuid

from bw.events.decoder import ServerSentEventBuilder


def test__server_sent_event_builder__with_event__splits_namespace_and_event():
    builder = ServerSentEventBuilder()
    builder.with_event('mission:uploaded')
    assert builder.namespace == 'mission'
    assert builder.event == 'uploaded'


def test__server_sent_event_builder__finish__without_id_uses_nil_uuid():
    event = ServerSentEventBuilder().finish()
    assert event.id == uuid.UUID(int=0)


def test__server_sent_event_builder__finish__with_id_parses_hex():
    builder = ServerSentEventBuilder()
    builder.with_id('11111111222233334444555555555555')
    event = builder.finish()
    assert event.id == uuid.UUID(hex='11111111222233334444555555555555')


def test__server_sent_event_builder__with_data__round_trips_payload():
    builder = ServerSentEventBuilder()
    builder.with_data({'foo': 'bar', 'count': 3})
    event = builder.finish()
    assert event.data == {'foo': 'bar', 'count': 3}


def test__server_sent_event_builder__finish__copies_event_and_namespace():
    builder = ServerSentEventBuilder()
    builder.with_event('mission:reviewed')
    event = builder.finish()
    assert event.namespace == 'mission'
    assert event.event == 'reviewed'
