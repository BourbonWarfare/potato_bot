# ruff: noqa: F401, F811

import pytest

from bw.events.broker import Broker
from tests.fixtures.events import make_event, uploaded_event, reviewed_event


class HandlerSpy:
    """Async callable that records every event it received."""

    def __init__(self):
        self.calls = []

    async def __call__(self, event):
        self.calls.append(event)


@pytest.mark.asyncio
async def test__broker__publish__matching_namespace_and_event_invokes_handler(uploaded_event):
    broker = Broker()
    spy = HandlerSpy()
    broker.add_handler(spy, namespace='mission', event='uploaded')

    await broker.publish(uploaded_event)

    assert spy.calls == [uploaded_event]


@pytest.mark.asyncio
async def test__broker__publish__namespace_mismatch_skips_handler(uploaded_event):
    broker = Broker()
    spy = HandlerSpy()
    broker.add_handler(spy, namespace='server', event='uploaded')

    await broker.publish(uploaded_event)

    assert spy.calls == []


@pytest.mark.asyncio
async def test__broker__publish__event_mismatch_skips_handler(uploaded_event):
    broker = Broker()
    spy = HandlerSpy()
    broker.add_handler(spy, namespace='mission', event='reviewed')

    await broker.publish(uploaded_event)

    assert spy.calls == []


@pytest.mark.asyncio
async def test__broker__publish__none_filters_match_all(uploaded_event, reviewed_event):
    broker = Broker()
    spy = HandlerSpy()
    broker.add_handler(spy, namespace=None, event=None)

    await broker.publish(uploaded_event)
    await broker.publish(reviewed_event)

    assert spy.calls == [uploaded_event, reviewed_event]


@pytest.mark.asyncio
async def test__broker__publish__namespace_only_filter_matches_any_event(uploaded_event, reviewed_event):
    broker = Broker()
    spy = HandlerSpy()
    broker.add_handler(spy, namespace='mission', event=None)

    await broker.publish(uploaded_event)
    await broker.publish(reviewed_event)

    assert spy.calls == [uploaded_event, reviewed_event]


@pytest.mark.asyncio
async def test__broker__publish__handler_exception_does_not_propagate(uploaded_event):
    broker = Broker()
    survivor = HandlerSpy()

    async def boom(_):
        raise RuntimeError('handler failed')

    broker.add_handler(boom, namespace=None, event=None)
    broker.add_handler(survivor, namespace=None, event=None)

    await broker.publish(uploaded_event)

    assert survivor.calls == [uploaded_event]


@pytest.mark.asyncio
async def test__broker__publish__multiple_matching_handlers_all_fire(uploaded_event):
    broker = Broker()
    one = HandlerSpy()
    two = HandlerSpy()
    broker.add_handler(one, namespace='mission', event='uploaded')
    broker.add_handler(two, namespace='mission', event=None)

    await broker.publish(uploaded_event)

    assert one.calls == [uploaded_event]
    assert two.calls == [uploaded_event]


def test__broker__add_handler__appends_to_handlers():
    broker = Broker()

    async def noop(_):
        return

    assert broker.handlers == []
    broker.add_handler(noop, namespace='mission', event='uploaded')
    assert len(broker.handlers) == 1
    assert broker.handlers[0].handler is noop
    assert broker.handlers[0].filtered_namespace == 'mission'
    assert broker.handlers[0].filtered_event == 'uploaded'
