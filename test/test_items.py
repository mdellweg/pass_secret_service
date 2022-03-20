import pytest

from dbus_next import DBusError, Variant

from pass_secret_service.common.names import bus_name, base_path

from .helper import get_collection, get_item, get_service, get_session


class TestCollection:
    @pytest.mark.asyncio
    async def test_create_delete_item(self, bus, pss_service):
        service = await get_service(bus)
        default_collection = await get_collection(bus, "/org/freedesktop/secrets/aliases/default")
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        item_path, prompt_path = await default_collection.call_create_item({}, [session_path, b"", b"password", "text/plain"], False)
        item = await get_item(bus, item_path)
        assert item_path in await default_collection.get_items()
        assert [session_path, b"", b"password", "text/plain"] == await item.call_get_secret(session_path)
        await item.call_set_secret([session_path, b"", b"secret", "text/plain"])
        assert [session_path, b"", b"secret", "text/plain"] == await item.call_get_secret(session_path)
        await item.call_delete()
        assert item_path not in await default_collection.get_items()
        await session.call_close()

    @pytest.mark.asyncio
    async def test_get_and_set_secret(self, bus, pss_service):
        service = await get_service(bus)
        default_collection = await get_collection(bus, "/org/freedesktop/secrets/aliases/default")
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        item_path, prompt_path = await default_collection.call_create_item({}, [session_path, b"", b"password", "text/plain"], False)
        item = await get_item(bus, item_path)
        assert [session_path, b"", b"password", "text/plain"] == await item.call_get_secret(session_path)
        await item.call_set_secret([session_path, b"", b"secret", "text/plain"])
        assert [session_path, b"", b"secret", "text/plain"] == await item.call_get_secret(session_path)
        await item.call_delete()
        await session.call_close()

    @pytest.mark.asyncio
    async def test_item_properties(self, bus, pss_service):
        service = await get_service(bus)
        default_collection = await get_collection(bus, "/org/freedesktop/secrets/aliases/default")
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        properties = {
            "org.freedesktop.Secret.Item.Label": Variant("s", "test_label"),
            "org.freedesktop.Secret.Item.Attributes": Variant("a{ss}", {"attr1": "val1"}),
        }
        item_path, prompt_path = await default_collection.call_create_item(properties, [session_path, b"", b"password", "text/plain"], False)
        item = await get_item(bus, item_path)
        assert await item.get_label() == "test_label"
        await item.set_label("test_label2")
        await item.set_label("test_label2")
        assert await item.get_label() == "test_label2"
        assert await item.get_attributes() == {"attr1": "val1"}
        await item.set_attributes({"attr1": "val2"})
        await item.set_attributes({"attr1": "val2"})
        assert await item.get_attributes() == {"attr1": "val2"}
        assert await item.get_locked() is False
        assert await item.get_created() == 0
        assert await item.get_modified() == 0
        await item.call_delete()
        await session.call_close()

    @pytest.mark.asyncio
    async def test_broken_session_path(self, bus, pss_service):
        service = await get_service(bus)
        default_collection = await get_collection(bus, "/org/freedesktop/secrets/aliases/default")
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        with pytest.raises(DBusError, match=r".*No such session:.*"):
            item_path, prompt_path = await default_collection.call_create_item({}, [session_path + "tilt", b"", b"password", "text/plain"], False)

        with pytest.raises(DBusError, match=r".*No such object:.*"):
            item_path, prompt_path = await default_collection.call_create_item({}, ["/tilt" + session_path, b"", b"password", "text/plain"], False)
        await session.call_close()

    @pytest.mark.asyncio
    async def test_item_lookup(self, bus, pss_service):
        service = await get_service(bus)
        default_collection = await get_collection(bus, "/org/freedesktop/secrets/aliases/default")
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        attributes = {"lookup_attr1": "1", "lookup_attr2": "2"}
        properties = {
            "org.freedesktop.Secret.Item.Label": Variant("s", "lookup_label1"),
            "org.freedesktop.Secret.Item.Attributes": Variant("a{ss}", attributes),
        }
        item_path, prompt_path = await default_collection.call_create_item(properties, [session_path, b"", b"password", "text/plain"], False)
        assert item_path in (await service.call_search_items({"lookup_attr1": "1"}))[0]
        assert item_path in (await service.call_search_items({"lookup_attr1": "1", "lookup_attr2": "2"}))[0]
        assert item_path not in (await service.call_search_items({"lookup_attr1": "1", "lookup_attr2": "0"}))[0]
        assert item_path not in (await service.call_search_items({"lookup_attr1": "1", "lookup_attr3": "3"}))[0]
        await session.call_close()

    @pytest.mark.asyncio
    async def test_item_in_deleted_collection(self, bus, pss_service):
        service = await get_service(bus)
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        collection_path, promt_path = await service.call_create_collection({}, "delete_alias")
        collection = await get_collection(bus, collection_path)
        properties = {
            "org.freedesktop.Secret.Item.Label": Variant("s", "delete_label1"),
        }
        item_path, prompt_path = await collection.call_create_item(properties, [session_path, b"", b"password", "text/plain"], False)
        assert item_path in (await service.call_search_items({}))[0]
        await collection.call_delete()
        assert item_path not in (await service.call_search_items({}))[0]
        await session.call_close()

    @pytest.mark.asyncio
    async def test_replace_item(self, bus, pss_service):
        service = await get_service(bus)
        default_collection = await get_collection(bus, "/org/freedesktop/secrets/aliases/default")
        dummy, session_path = await service.call_open_session("plain", Variant("s", ""))
        session = await get_session(bus, session_path)
        properties = {
            "org.freedesktop.Secret.Item.Label": Variant("s", "test_label"),
            "org.freedesktop.Secret.Item.Attributes": Variant("a{ss}", {"lookup_attr": "replace_test"}),
        }
        item1_path, prompt_path = await default_collection.call_create_item(properties, [session_path, b"", b"password1", "text/plain"], False)
        item2_path, prompt_path = await default_collection.call_create_item(properties, [session_path, b"", b"password2", "text/plain"], True)
        item3_path, prompt_path = await default_collection.call_create_item(properties, [session_path, b"", b"password3", "text/plain"], False)
        assert item1_path == item2_path
        assert item1_path != item3_path
        await session.call_close()
