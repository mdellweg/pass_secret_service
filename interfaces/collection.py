# Implementation of the org.freedesktop.Secret.Collection interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib
from common.debug import debug_me

from common.names import base_path
from interfaces.item import Item

LABEL_INTERFACE = 'org.freedesktop.Secret.Collection.Label'

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

    @debug_me
    def __init__(self, parent, properties=None, name=None):
        self.properties = properties or {}
        self.parent = parent
        self.bus = self.parent.bus
        self.pass_store = self.parent.pass_store
        if name:
            # collection exists with given Name
            self.name = name
        else:
            # collection must be created
            self.name = self.pass_store.create_collection(self.properties)
        self.properties = self.pass_store.get_collection_properties(self.name)
        self.path = base_path + '/collection/' + self.name
        self.pub_ref = self.bus.register_object(self.path, self, None)
        self.parent.collections[self.name] = self

    @debug_me
    def Delete(self):
        self.pub_ref.unregister()
        self.parent.collections.pop(self.name)
        self.pass_store.delete_collection(self.name)
        self.parent.CollectionDeleted(self.path)
        deleted_aliases = [ name for name, alias in self.parent.aliases.items() if alias['collection'] == self ]
        for name in deleted_aliases:
            self.parent._set_alias(name, None)
        if len(deleted_aliases) > 0:
            self.parent._write_aliases()
        prompt = "/"
        return prompt

    @debug_me
    def SearchItems(self, attributes):
        results = []
        return results

    @debug_me
    def CreateItem(self, properties, secret, replace):
        new_item = Item(self.bus, self.label, 'item1')
        item = new_item.path
        prompt = '/'
        return item, prompt

    ItemCreated = signal()
    ItemDeleted = signal()
    ItemChanged = signal()

    @property
    def Items(self):
        return []

    @property
    def Label(self):
        return str(self.properties.get(LABEL_INTERFACE))

    @Label.setter
    def Label(self, label):
        if self.Label != label:
            self.properties = self.pass_store.update_collection_properties(self.name, {LABEL_INTERFACE: label})

    @property
    def Locked(self):
        return False

    @property
    def Created(self):
        return 0

    @property
    def Modified(self):
        return 0
