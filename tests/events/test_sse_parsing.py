import uuid

from bw.events.broker import apply_sse_line
from bw.events.decoder import ServerSentEventBuilder


def test__apply_sse_line__ignores_comment_lines():
    builder = ServerSentEventBuilder()

    result = apply_sse_line(builder, ': keepalive')

    assert result is builder
    assert builder.finish().id == uuid.UUID(int=0)


def test__apply_sse_line__ignores_lines_without_separator():
    builder = ServerSentEventBuilder()

    result = apply_sse_line(builder, 'not valid sse')

    assert result is builder
    assert builder.finish().event is None


def test__apply_sse_line__loads_json_data():
    builder = ServerSentEventBuilder()

    apply_sse_line(builder, 'event: uploaded')
    apply_sse_line(builder, 'data: {"mission": "abc"}')

    event = builder.finish()
    assert event.event == 'uploaded'
    assert event.data == {'mission': 'abc'}
