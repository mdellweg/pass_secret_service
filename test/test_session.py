import asyncio
import pytest

from dbus_next import DBusError, Variant
from dbus_next.aio import MessageBus

from .helper import get_service, get_session


class TestSession():
    @pytest.mark.asyncio
    async def test_session_plain(self, bus, pss_service):
        service = await get_service(bus)
        output, session_path = await service.call_open_session('plain', Variant('s', ''))
        assert output == Variant('s', '')
        session = await get_session(bus, session_path)
        await session.call_close()

    @pytest.mark.asyncio
    async def test_session_error(self, bus, pss_service):
        service = await get_service(bus)
        with pytest.raises(DBusError):
            output, session_path = await service.call_open_session('wrong plain', Variant('s', ''))

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
