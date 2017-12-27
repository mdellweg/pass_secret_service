# Implementation of the org.freedesktop.Secret.Collection interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib

from pass_secret_service.common.debug import debug_me
from pass_secret_service.common.names import base_path, COLLECTION_LABEL, ITEM_LABEL, ITEM_ATTRIBUTES
from pass_secret_service.interfaces.item import Item


class Collection(object):
    """
      <node>
        <interface name='org.freedesktop.Secret.Collection'>
          <method name='Delete'>
            <arg type='o' name='prompt' direction='out'/>
          </method>
          <method name='SearchItems'>
            <arg type='a{ss}' name='attributes' direction='in'/>
            <arg type='ao' name='results' direction='out'/>
          </method>
          <method name='CreateItem'>
            <arg type='a{sv}' name='properties' direction='in'/>
            <arg type='(oayays)' name='secret' direction='in'/>
            <arg type='b' name='replace' direction='in'/>
            <arg type='o' name='item' direction='out'/>
            <arg type='o' name='prompt' direction='out'/>
          </method>
          <signal name='ItemCreated'>
            <arg type='o' name='item' direction='out'/>
          </signal>
          <signal name='ItemDeleted'>
            <arg type='o' name='item' direction='out'/>
          </signal>
          <signal name='ItemChanged'>
            <arg type='o' name='item' direction='out'/>
          </signal>
          <property name='Items' type='ao' access='read' />
          <property name='Label' type='s' access='readwrite' />
          <property name='Locked' type='b' access='read' />
          <property name='Created' type='t' access='read' />
          <property name='Modified' type='t' access='read' />
        </interface>
      </node>
    """

    @classmethod
    def _create(cls, service, properties):
        name = service.pass_store.create_collection(properties)
        instance = cls(service, name)
        service.CollectionCreated(instance.path)
        return instance

    def _lock(self):
        self.locked = True

    def _unlock(self):
        self.locked = False

    def _unregister(self):
        for item in self.items.values():
            item._unregister()
        self.pub_ref.unregister()

    @debug_me
    def __init__(self, service, name):
        self.service = service
        self.bus = self.service.bus
        self.pass_store = self.service.pass_store
        self.name = name
        self.properties = self.pass_store.get_collection_properties(self.name)
        self.path = base_path + '/collection/' + self.name
        self.locked = False
        self.items = {}
        for item_name in self.pass_store.get_items(self.name):
            Item(self, item_name)
        # Register with dbus
        self.pub_ref = self.bus.register_object(self.path, self, None)
        # Register with service
        self.service.collections[self.name] = self

    @debug_me
    def Delete(self):
        # Delete items
        for item in list(self.items.values()):
            item.Delete()
        # Remove stale aliases
        deleted_aliases = [name for name, alias in self.service.aliases.items() if alias['collection'] == self]
        self.service._set_aliases({name: None for name in deleted_aliases})
        # Deregister from servise
        self.service.collections.pop(self.name)
        # Deregister from dbus
        self._unregister()
        # Remove from disk
        self.pass_store.delete_collection(self.name)
        # Signal deletion
        self.service.CollectionDeleted(self.path)
        prompt = "/"
        return prompt

    @debug_me
    def SearchItems(self, attributes):
        results = []
        for item in self.items.values():
            if item._has_attributes(attributes):
                results.append(item.path)
        return results

    @debug_me
    def CreateItem(self, properties, secret, replace):
        prompt = '/'
        if replace:
            attributes = properties.get(ITEM_ATTRIBUTES, {})
            repl_items = self.SearchItems(attributes)
            if len(repl_items):
                item = self.service._get_item_from_path(repl_items[0])
                item.Label = properties.get(ITEM_LABEL, '')
                item.SetSecret(secret)
                return item.path, prompt
        password = self.service._decode_secret(secret)
        item = Item._create(self, password, properties)
        return item.path, prompt

    ItemCreated = signal()
    ItemDeleted = signal()
    ItemChanged = signal()

    @property
    def Items(self):
        return [item.path for item in self.items.values()]

    @property
    def Label(self):
        return str(self.properties.get(COLLECTION_LABEL))

    @Label.setter
    def Label(self, label):
        if self.Label != label:
            self.properties = self.pass_store.update_collection_properties(self.name, {COLLECTION_LABEL: label})
            self.service.CollectionChanged(self.path)

    @property
    def Locked(self):
        return self.locked

    @property
    def Created(self):
        return 0

    @property
    def Modified(self):
        return 0

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
