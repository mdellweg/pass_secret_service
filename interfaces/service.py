# Implementation of the org.freedesktop.Secret.Service interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib

from common.debug import debug_me
from common.exceptions import DBusErrorNotSupported
from common.names import bus_name, base_path
from interfaces.collection import Collection
from interfaces.session import Session

class Service:
    """
      <node>
        <interface name='org.freedesktop.Secret.Service'>
          <method name='OpenSession'>
            <arg type='s' name='algorithm' direction='in'/>
            <arg type='v' name='input' direction='in'/>
            <arg type='v' name='output' direction='out'/>
            <arg type='o' name='result' direction='out'/>
          </method>
          <method name='CreateCollection'>
            <arg type='a{sv}' name='properties' direction='in'/>
            <arg type='s' name='alias' direction='in'/>
            <arg type='o' name='collection' direction='out'/>
            <arg type='o' name='prompt' direction='out'/>
          </method>
          <method name='SearchItems'>
            <arg type='a{ss}' name='attributes' direction='in'/>
            <arg type='ao' name='unlocked' direction='out'/>
            <arg type='ao' name='locked' direction='out'/>
          </method>
          <method name='Unlock'>
            <arg type='ao' name='objects' direction='in'/>
            <arg type='ao' name='unlocked' direction='out'/>
            <arg type='o' name='prompt' direction='out'/>
          </method>
          <method name='Lock'>
            <arg type='ao' name='objects' direction='in'/>
            <arg type='ao' name='locked' direction='out'/>
            <arg type='o' name='prompt' direction='out'/>
          </method>
          <method name='GetSecrets'>
            <arg type='ao' name='items' direction='in'/>
            <arg type='o' name='session' direction='in'/>
            <arg type='a{o(oayays)}' name='secrets' direction='out'/>
          </method>
          <method name='ReadAlias'>
            <arg type='s' name='name' direction='in'/>
            <arg type='o' name='collection' direction='out'/>
          </method>
          <method name='SetAlias'>
            <arg type='s' name='name' direction='in'/>
            <arg type='o' name='collection' direction='in'/>
          </method>
          <signal name='CollectionCreated'>
            <arg type='o' name='collection' direction='out'/>
          </signal>
          <signal name='CollectionDeleted'>
            <arg type='o' name='collection' direction='out'/>
          </signal>
          <signal name='CollectionChanged'>
            <arg type='o' name='collection' direction='out'/>
          </signal>
          <property name='Collections' type='ao' access='read'/>
        </interface>
      </node>
    """

    @debug_me
    def __init__(self, bus):
        self.bus = bus
        self.pub_ref = bus.publish(bus_name, self)
        self.collections = []

    @debug_me
    def OpenSession(self, algorithm, input):
        if algorithm != 'plain':
            raise DBusErrorNotSupported('only algorithm plain is implemented')
        output = GLib.Variant('s', '')
        new_session = Session(self.bus)
        result = new_session.path
        return output, result

    @debug_me
    def CreateCollection(self, properties, alias):
        collection = Collection(self, properties)
        self.collections.append(collection.path)
        self.CollectionCreated(collection.path)
        prompt = '/'
        return collection.path, prompt

    @debug_me
    def SearchItems(self, attributes):
        unlocked = []
        locked = []
        return unlocked, locked

    @debug_me
    def Unlock(self, objects):
        unlocked = []
        prompt = '/'
        return unlocked, prompt

    @debug_me
    def Lock(self, objects):
        locked = []
        prompt = '/'
        return locked, prompt
    @debug_me
    def GetSecrets(self, items, session):
        secrets = {}
        return secrets

    @debug_me
    def ReadAlias(self, name):
        collection = '/'
        return collection

    @debug_me
    def SetAlias(self, name, collection):
        return None

    CollectionCreated = signal()
    CollectionDeleted = signal()
    CollectionChanged = signal()

    @property
    @debug_me
    def Collections(self):
        return self.collections
