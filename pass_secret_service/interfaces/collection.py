# Implementation of the org.freedesktop.Secret.Collection interface

from dbus_next import Variant

from dbus_next.service import (
    dbus_property,
    method,
    PropertyAccess,
    ServiceInterface,
    signal,
)

from pass_secret_service.common.names import base_path, COLLECTION_LABEL, ITEM_LABEL, ITEM_ATTRIBUTES
from pass_secret_service.common.tools import run_in_executor
from pass_secret_service.interfaces.item import Item


class Collection(ServiceInterface):
    @staticmethod
    @run_in_executor
    def _create_in_store(service, properties):
        return service.pass_store.create_collection(properties)

    @classmethod
    async def _create(cls, service, properties):
        id = await cls._create_in_store(service, properties)
        instance = await cls._init(service, id)
        service.CollectionCreated(instance)
        return instance

    @run_in_executor
    def _delete_from_store(self):
        self.pass_store.delete_collection(self.id)

    def _lock(self):
        self.locked = True

    def _unlock(self):
        self.locked = False

    def _search_items(self, attributes):
        results = []
        for item in self.items.values():
            if item._has_attributes(attributes):
                results.append(item.path)
        return results

    async def _unregister(self):
        for item in self.items.values():
            await item._unregister()
        self.bus.unexport(self.path)

    def __init__(self, service, id):
        super().__init__('org.freedesktop.Secret.Collection')
        self.service = service
        self.bus = self.service.bus
        self.pass_store = self.service.pass_store
        self.id = id
        self.path = base_path + '/collection/' + self.id
        self.locked = False
        self.items = {}

    @run_in_executor
    def _get_collection_properties(self):
        return self.pass_store.get_collection_properties(self.id)

    @run_in_executor
    def _get_items(self):
        return self.pass_store.get_items(self.id)

    @classmethod
    async def _init(cls, service, id):
        self = cls(service, id)
        self.properties = await self._get_collection_properties()
        for item_id in await self._get_items():
            await Item._init(self, item_id)
        # Register with dbus
        self.pub_ref = self.bus.export(self.path, self)
        # Register with service
        self.service.collections[self.id] = self
        return self

    @method()
    async def Delete(self) -> 'o':
        # Delete items
        for item in list(self.items.values()):
            await item._delete()
        # Remove stale aliases
        deleted_aliases = [name for name, alias in self.service.aliases.items() if alias['collection'] == self]
        await self.service._set_aliases({name: None for name in deleted_aliases})
        # Deregister from servise
        self.service.collections.pop(self.id)
        # Deregister from dbus
        await self._unregister()
        # Remove from disk
        await self._delete_from_store()
        # Signal deletion
        self.service.CollectionDeleted(self)
        prompt = "/"
        return prompt

    @method()
    async def SearchItems(self, attributes: 'a{ss}') -> 'ao':
        return self._search_items(attributes)

    @method()
    async def CreateItem(self, properties: 'a{sv}', secret: '(oayays)', replace: 'b') -> 'oo':
        prompt = '/'
        if replace:
            attributes = properties.get(ITEM_ATTRIBUTES, Variant('a{ss}', {})).value
            repl_items = self._search_items(attributes)
            if len(repl_items):
                item = self.service._get_item_from_path(repl_items[0])
                item.Label = properties.get(ITEM_LABEL, Variant('s', '')).value
                await item._set_secret(secret)
                return [item.path, prompt]
        password = await self.service._decode_secret(secret)
        item = await Item._create(self, password, properties)
        return [item.path, prompt]

    @signal()
    def ItemCreated(self, item) -> 'o':
        return item.path

    @signal()
    def ItemDeleted(self, item) -> 'o':
        return item.path

    @signal()
    def ItemChanged(self, item) -> 'o':
        return item.path

    @dbus_property(access=PropertyAccess.READ)
    def Items(self) -> 'ao':
        return [item.path for item in self.items.values()]

    @dbus_property(access=PropertyAccess.READWRITE)
    def Label(self) -> 's':
        return str(self.properties.get(COLLECTION_LABEL))

    @Label.setter
    def Label(self, label: 's'):
        if self.Label != label:
            self.properties = self.pass_store.update_collection_properties(self.id, {COLLECTION_LABEL: label})
            self.service.CollectionChanged(self)

    @dbus_property(access=PropertyAccess.READ)
    def Locked(self) -> 'b':
        return self.locked

    @dbus_property(access=PropertyAccess.READ)
    def Created(self) -> 't':
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def Modified(self) -> 't':
        return 0
