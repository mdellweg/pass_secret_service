import asyncio
import pytest
import re

from dbus_next import DBusError, Variant
from dbus_next.aio import MessageBus

from pass_secret_service.common.names import bus_name, base_path

from .helper import (
    get_collection,
    get_service,
)


class TestService():
    @pytest.mark.asyncio
    async def test_collections_property(self, bus, pss_service):
        service = await get_service(bus)
        assert await service.call_read_alias('default') in await service.get_collections()

    @pytest.mark.asyncio
    async def test_get_default_collection(self, bus, pss_service):
        collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/default')
        assert 'default collection' == await collection.get_label()

    @pytest.mark.asyncio
    async def test_read_alias(self, bus, pss_service):
        service = await get_service(bus)
        assert re.match('/org/freedesktop/secrets/collection/.*', await service.call_read_alias('default'))
        assert '/' == await service.call_read_alias('defect')

    @pytest.mark.asyncio
    async def test_set_alias(self, bus, pss_service):
        service = await get_service(bus)
        ALIAS = 'aabb'
        TRACER = 'ccdd'
        collection_path1, prompt_path = await service.call_create_collection({}, '')
        collection_path2, prompt_path = await service.call_create_collection({'org.freedesktop.Secret.Collection.Label': Variant('s', TRACER)}, '')
        collection1 = await get_collection(bus, collection_path1)
        collection2 = await get_collection(bus, collection_path2)
        await service.call_set_alias(ALIAS, collection_path1)
        assert collection_path1 == await service.call_read_alias(ALIAS)
        await service.call_set_alias(ALIAS, '/')
        assert '/' == await service.call_read_alias(ALIAS)
        await service.call_set_alias(ALIAS, collection_path1)
        await service.call_set_alias(ALIAS, collection_path2)
        await service.call_set_alias(ALIAS, collection_path2)
        assert collection_path2 == await service.call_read_alias(ALIAS)
        collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/' + ALIAS)
        assert TRACER == await collection.get_label()
        await collection1.call_delete()
        assert collection_path2 == await service.call_read_alias(ALIAS)
        await collection2.call_delete()
        assert '/' == await service.call_read_alias(ALIAS)

    @pytest.mark.asyncio
    async def test_get_secrets(self, bus, pss_service):
        service = await get_service(bus)
        collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/default')
        prompt_path, session_path = await service.call_open_session('plain', Variant('s', ''))
        item1_path, prompt_path = await collection.call_create_item({}, [session_path, b'', b'password1', 'text/plain'], False)
        item2_path, prompt_path = await collection.call_create_item({}, [session_path, b'', b'password2', 'text/plain'], False)
        secrets = await service.call_get_secrets([item1_path, item2_path], session_path)
        assert 2 == len(secrets)
        assert b'password1' == secrets[item1_path][2]
        assert b'password2' == secrets[item2_path][2]

    @pytest.mark.asyncio
    async def test_lock_unlock_collection(self, bus, pss_service):
        service = await get_service(bus)
        locked, dummy = await service.call_lock(['/org/freedesktop/secrets/aliases/default', '/org/freedesktop/secrets/aliases/nodefault', '/'])
        assert '/org/freedesktop/secrets/aliases/default' in locked
        assert '/org/freedesktop/secrets/aliases/nodefault' not in locked
        assert '/' not in locked
        unlocked, dummy = await service.call_unlock(['/org/freedesktop/secrets/aliases/default', '/org/freedesktop/secrets/aliases/nodefault', '/'])
        assert '/org/freedesktop/secrets/aliases/default' in unlocked
        assert '/org/freedesktop/secrets/aliases/nodefault' not in unlocked
        assert '/' not in unlocked
        unlocked, dummy = await service.call_unlock(['/org/freedesktop/secrets/collection/nodefault/test', await service.call_read_alias('default') + '/test'])
        assert [] == unlocked
        unlocked, dummy = await service.call_unlock(['/org/freedesktop/secrets/nocollection/default'])
        assert [] == unlocked

    @pytest.mark.asyncio
    async def test_empty_session(self, bus, pss_service):
        collection = await get_collection(bus, '/org/freedesktop/secrets/aliases/default')
        with pytest.raises(DBusError):
            item_path, prompt_path = await collection.call_create_item({}, ['/', b'', b'password1', 'text/plain'], False)
        with pytest.raises(DBusError):
            item_path, prompt_path = await collection.call_create_item({}, ['/org/freedesktop/secrets/nosession/test', b'', b'password1', 'text/plain'], False)

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
