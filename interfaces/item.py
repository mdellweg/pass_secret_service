# Implementation of the org.freedesktop.Secret.Item interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib
from common.debug import debug_me

from common.names import base_path

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
    
    @debug_me
    def __init__(self, bus, collection_label, label):
        self.bus = bus
        self.label = label
        self.path = base_path + '/collection/' + collection_label + '/' + label
        self.pub_ref = bus.register_object(self.path, self, None)

    @debug_me
    def Delete(self):
        self.pub_ref.unregister()
        # TODO actually delete
        # TODO signal deletion
        prompt = "/"
        return prompt

    @debug_me
    def GetSecret(self, session):
        secret = ''
        return secret

    @debug_me
    def SetSecret(self, secret):
        return None

    @property
    def Locked(self):
        return False

    @property
    def Attributes(self):
        return {}

    @Attributes.setter
    def Attributes(self, attributes):
        pass

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
    def Created(self):
        return 0

    @property
    def Modified(self):
        return 0
