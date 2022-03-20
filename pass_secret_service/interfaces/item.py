# Implementation of the org.freedesktop.Secret.Item interface

from dbus_next.service import (
    dbus_property,
    method,
    PropertyAccess,
    ServiceInterface,
)

from pass_secret_service.common.names import base_path, ITEM_LABEL, ITEM_ATTRIBUTES
from pass_secret_service.common.tools import run_in_executor


class Item(ServiceInterface):
    @classmethod
    @run_in_executor
    def _create_in_store(cls, collection, password, properties):
        return collection.service.pass_store.create_item(collection.id, password, properties)

    @classmethod
    async def _create(cls, collection, password, properties=None):
        if properties is None:
            properties = {}
        else:
            properties = {k: v.value for k, v in properties.items()}
        id = await cls._create_in_store(collection, password, properties)
        instance = await cls._init(collection, id)
        collection.ItemCreated(instance)
        return instance

    @run_in_executor
    def _delete_from_store(self):
        self.service.pass_store.delete_item(self.collection.id, self.id)

    async def _delete(self):
        # Deregister from collection
        self.collection.items.pop(self.id)
        # Deregister from dbus
        await self._unregister()
        # Remove from disk
        await self._delete_from_store()
        # Signal deletion
        self.collection.ItemDeleted(self)

    def _has_attributes(self, attributes):
        attrs = self.Attributes
        for key, value in attributes.items():
            if key not in attrs or attrs[key] != value:
                return False
        return True

    @run_in_executor
    def _get_password(self):
        return self.pass_store.get_item_password(self.collection.id, self.id)

    async def _get_secret(self, session):
        password = await self._get_password()
        return await self.service._encode_secret(session, password)

    @run_in_executor
    def _set_password(self, password):
        return self.pass_store.set_item_password(self.collection.id, self.id, password)

    async def _set_secret(self, secret):
        password = await self.service._decode_secret(secret)
        await self._set_password(password)
        self.collection.ItemChanged(self)

    async def _unregister(self):
        self.bus.unexport(self.path)

    def __init__(self, collection, id):
        super().__init__('org.freedesktop.Secret.Item')
        self.collection = collection
        self.service = self.collection.service
        self.bus = self.service.bus
        self.pass_store = self.service.pass_store
        self.id = id
        self.path = self.collection.path + '/' + self.id

    @run_in_executor
    def _get_item_properties(self):
        return self.pass_store.get_item_properties(self.collection.id, self.id)

    @classmethod
    async def _init(cls, collection, id):
        self = cls(collection, id)
        self.properties = await self._get_item_properties()
        # Register with dbus
        self.bus.export(self.path, self)
        # Register with collection
        self.collection.items[self.id] = self
        return self

    @method()
    async def Delete(self) -> 'o':
        await self._delete()
        prompt = '/'
        return prompt

    @method()
    async def GetSecret(self, session: 'o') -> '(oayays)':
        return await self._get_secret(session)

    @method()
    async def SetSecret(self, secret: '(oayays)'):
        await self._set_secret(secret)

    @dbus_property(access=PropertyAccess.READ)
    def Locked(self) -> 'b':
        return False

    @dbus_property(access=PropertyAccess.READWRITE)
    def Attributes(self) -> 'a{ss}':
        return self.properties.get(ITEM_ATTRIBUTES, {})

    @Attributes.setter
    def Attributes(self, attributes: 'a{ss}'):
        if self.Attributes != attributes:
            self.properties = self.pass_store.update_item_properties(self.collection.id, self.id, {ITEM_ATTRIBUTES: attributes})
            self.collection.ItemChanged(self)
            self.emit_properties_changed({'Attributes': attributes})

    @dbus_property(access=PropertyAccess.READWRITE)
    def Label(self) -> 's':
        return str(self.properties.get(ITEM_LABEL, ''))

    @Label.setter
    def Label(self, label: 's'):
        if self.Label != label:
            self.properties = self.pass_store.update_item_properties(self.collection.id, self.id, {ITEM_LABEL: label})
            self.collection.ItemChanged(self)
            self.emit_properties_changed({'Label': label})

    @dbus_property(access=PropertyAccess.READ)
    def Created(self) -> 't':
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def Modified(self) -> 't':
        return 0
