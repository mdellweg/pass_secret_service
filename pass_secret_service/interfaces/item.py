# Implementation of the org.freedesktop.Secret.Item interface

from dbus_next.service import (
    dbus_property,
    method,
    PropertyAccess,
    ServiceInterface,
)

from pass_secret_service.common.names import base_path, ITEM_LABEL, ITEM_ATTRIBUTES


class Item(ServiceInterface):
    @classmethod
    def _create(cls, collection, password, properties=None):
        if properties is None:
            properties = {}
        else:
            properties = {k: v.value for k, v in properties.items()}
        id = collection.service.pass_store.create_item(collection.id, password, properties)
        instance = cls(collection, id)
        collection.ItemCreated(instance)
        return instance

    def _has_attributes(self, attributes):
        attrs = self.Attributes
        for key, value in attributes.items():
            if key not in attrs or attrs[key] != value:
                return False
        return True

    def _get_password(self):
        return self.pass_store.get_item_password(self.collection.id, self.id)

    def _set_secret(self, secret):
        password = self.service._decode_secret(secret)
        self.pass_store.set_item_password(self.collection.id, self.id, password)
        self.collection.ItemChanged(self)

    def _unregister(self):
        self.bus.unexport(self.path)

    def __init__(self, collection, id):
        super().__init__('org.freedesktop.Secret.Item')
        self.collection = collection
        self.service = self.collection.service
        self.bus = self.service.bus
        self.pass_store = self.service.pass_store
        self.id = id
        self.properties = self.pass_store.get_item_properties(self.collection.id, self.id)
        self.path = self.collection.path + '/' + self.id
        # Register with dbus
        self.bus.export(self.path, self)
        # Register with collection
        self.collection.items[self.id] = self

    @method()
    def Delete(self) -> 'o':
        # Deregister from collection
        self.collection.items.pop(self.id)
        # Deregister from dbus
        self._unregister()
        # Remove from disk
        self.service.pass_store.delete_item(self.collection.id, self.id)
        # Signal deletion
        self.collection.ItemDeleted(self)
        prompt = '/'
        return prompt

    @method()
    def GetSecret(self, session: 'o') -> '(oayays)':
        return self.service._encode_secret(session, self._get_password())

    @method()
    def SetSecret(self, secret: '(oayays)'):
        self._set_secret(secret)

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

    @dbus_property(access=PropertyAccess.READWRITE)
    def Label(self) -> 's':
        return str(self.properties.get(ITEM_LABEL, ''))

    @Label.setter
    def Label(self, label: 's'):
        if self.Label != label:
            self.properties = self.pass_store.update_item_properties(self.collection.id, self.id, {ITEM_LABEL: label})
            self.collection.ItemChanged(self)

    @dbus_property(access=PropertyAccess.READ)
    def Created(self) -> 't':
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def Modified(self) -> 't':
        return 0

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
