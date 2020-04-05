import asyncio
import pytest

from dbus_next import DBusError, Variant
from dbus_next.aio import MessageBus

from pass_secret_service.common.names import bus_name, base_path
from .helper import get_collection, get_service, ServiceEnv


class TestCollection():
    @pytest.mark.asyncio
    async def test_create_delete_collection(self, bus, pss_service):
        service = await get_service(bus)
        properties = {'org.freedesktop.Secret.Collection.Label': Variant('s', 'test_collection_label')}
        collection_path, prompt_path = await service.call_create_collection(properties, 'test_alias')
        collection = await get_collection(bus, collection_path)
        assert await collection.get_label() == 'test_collection_label'
        assert collection_path in await service.get_collections()
        assert await service.call_read_alias('test_alias') == collection_path
        await collection.call_delete()
        assert collection_path not in await service.get_collections()

    @pytest.mark.asyncio
    async def test_properties(self, bus, pss_service):
        collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/default')
        await collection.get_label()
        await collection.get_locked()
        await collection.get_created()
        await collection.get_modified()

    @pytest.mark.asyncio
    async def test_lock_unlock(self, bus, pss_service):
        service = await get_service(bus)
        properties = {'org.freedesktop.Secret.Collection.Label': Variant('s', 'test_lock_label')}
        collection_path, prompt_path = await service.call_create_collection(properties, '')
        collection = await get_collection(bus, collection_path)
        await service.call_lock([collection_path])
        assert await collection.get_locked() is True
        await service.call_unlock([collection_path])
        assert await collection.get_locked() is False

    @pytest.mark.asyncio
    async def test_persisted_item(self, bus):
        async with ServiceEnv():
            service = await get_service(bus)
            default_collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/default')
            dummy, session_path = await service.call_open_session('plain', Variant('s', ''))
            await default_collection.call_create_item({}, [session_path, b'', b'password', 'text/plain'], True)
        async with ServiceEnv(clean=False):
            service = await get_service(bus)
            default_collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/default')
            assert len(await default_collection.get_items()) == 1

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
