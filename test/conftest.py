import asyncio
import pytest_asyncio

from dbus_next.aio import MessageBus

from pass_secret_service.common.names import base_path, bus_name
from pass_secret_service.common.pass_store import PassStore
from pass_secret_service.interfaces.service import Service

from .helper import ServiceEnv


@pytest_asyncio.fixture
async def pss_service():
    async with ServiceEnv():
        yield True


@pytest_asyncio.fixture
async def bus():
    bus = await MessageBus().connect()
    yield bus
    bus.disconnect()
