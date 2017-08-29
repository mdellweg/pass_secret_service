# Implementation of the org.freedesktop.Secret.Collection interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib
from common.debug import debug_me

from common.names import base_path
from interfaces.item import Item

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
            <arg type='o' name='secret' direction='in'/>
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
    def __init__(self, bus, label):
        self.bus = bus
        self.label = label
        self.path = base_path + '/collection/' + label
        self.pub_ref = bus.register_object(self.path, self, None)

    @debug_me
    def Delete(self):
        self.pub_ref.unregister()
        #TODO actually delete
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
        return self.label

    @Label.setter
    def Label(self, label):
        if self.label != label:
            self.pub_ref.unregister()
            self.label = label
            self.path = base_path + '/collection/' + label
            self.pub_ref = bus.register_object(self.path, self, None)

    @property
    def Locked(self):
        return False

    @property
    def Created(self):
        return 0

    @property
    def Modified(self):
        return 0
