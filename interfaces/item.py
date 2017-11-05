# Implementation of the org.freedesktop.Secret.Item interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib
from common.debug import debug_me

from common.names import base_path

LABEL_INTERFACE = 'org.freedesktop.Secret.Item.Label'
ATTRIBUTES_INTERFACE = 'org.freedesktop.Secret.Item.Attributes'

class Item(object):
    """
      <node>
        <interface name='org.freedesktop.Secret.Item'>
          <method name='Delete'>
            <arg type='o' name='prompt' direction='out'/>
          </method>
          <method name='GetSecret'>
            <arg type='o' name='session' direction='in'/>
            <arg type='(oayays)' name='secret' direction='out'/>
          </method>
          <method name='SetSecret'>
            <arg type='(oayays)' name='secret' direction='in'/>
          </method>
          <property name='Locked' type='b' access='read'/>
          <property name='Attributes' type='a{ss}' access='readwrite'/>
          <property name='Label' type='s' access='readwrite'/>
          <property name='Created' type='t' access='read'/>
          <property name='Modified' type='t' access='read'/>
        </interface>
      </node>
    """

    @classmethod
    def _create(cls, collection, password, properties=None):
        if properties is None:
            properties = {}  # pragma: no cover
        name = collection.service.pass_store.create_item(collection.name, password, properties)
        instance = cls(collection, name)
        collection.ItemCreated(instance.path)
        return instance

    def _has_attributes(self, attributes):
        attrs = self.Attributes
        for key, value in attributes.items():
            if key not in attrs or attrs[key] != value:
                return False
        return True

    @debug_me
    def __init__(self, collection, name):
        self.collection = collection
        self.service = self.collection.service
        self.bus = self.service.bus
        self.pass_store = self.service.pass_store
        self.name = name
        self.properties = self.pass_store.get_item_properties(self.collection.name, self.name)
        self.path = self.collection.path + '/' + self.name
        # Register with dbus
        self.pub_ref = self.bus.register_object(self.path, self, None)
        # Register with collection
        self.collection.items[self.name] = self

    @debug_me
    def Delete(self):
        # Deregister from collection
        self.collection.items.pop(self.name)
        # Deregister from dbus
        self.pub_ref.unregister()
        # Remove from disk
        self.service.pass_store.delete_item(self.collection.name, self.name)
        # Signal deletion
        self.collection.ItemDeleted(self.path)
        prompt = '/'
        return prompt

    @debug_me
    def GetSecret(self, session):
        password = self.pass_store.get_item_password(self.collection.name, self.name)
        return self.service._encode_secret(session, password)

    @debug_me
    def SetSecret(self, secret):
        password = self.service._decode_secret(secret)
        self.pass_store.set_item_password(self.collection.name, self.name, password)
        self.collection.ItemChanged(self.path)

    @property
    def Locked(self):
        return False

    @property
    def Attributes(self):
        return self.properties.get(ATTRIBUTES_INTERFACE, {})

    @Attributes.setter
    def Attributes(self, attributes):
        if self.Attributes != attributes:
            self.properties = self.pass_store.update_item_properties(self.collection.name, self.name, {ATTRIBUTES_INTERFACE: attributes})
            self.collection.ItemChanged(self.path)

    @property
    def Label(self):
        return str(self.properties.get(LABEL_INTERFACE, ''))

    @Label.setter
    def Label(self, label):
        if self.Label != label:
            self.properties = self.pass_store.update_item_properties(self.collection.name, self.name, {LABEL_INTERFACE: label})
            self.collection.ItemChanged(self.path)

    @property
    def Created(self):
        return 0

    @property
    def Modified(self):
        return 0

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
