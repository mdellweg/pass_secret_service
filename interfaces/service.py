# Implementation of the org.freedesktop.Secret.Service interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib

from common.debug import debug_me
from common.exceptions import DBusErrorNotSupported
from common.names import bus_name, base_path
from interfaces.collection import Collection, LABEL_INTERFACE
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

    def _set_alias(self, alias, collection):
        changed = False
        old_alias = self.aliases.get(alias)
        if old_alias:
            if old_alias['collection'] == collection:
                return changed
            old_alias['pub_ref'].unregister()
            self.aliases.pop(alias)
            changed = True
        if collection:
            alias_path = base_path + '/aliases/' + alias
            alias_ref = self.bus.register_object(alias_path, collection, None)
            self.aliases[alias] = { 'collection': collection, 'pub_ref': alias_ref }
            changed = True
        return changed

    def _write_aliases(self):
        self.pass_store.save_aliases({key: value['collection'].name for key, value in self.aliases.items()})

    def _set_aliases(self, alias_dict):
        changed = False
        for alias, collection in alias_dict.items():
            if self._set_alias(alias, collection):
                changed = True
        if changed:
            self._write_aliases()

    def _get_collection_from_path(self, collection_path):
        if collection_path == '/':
            return None
        collection = self.collections.get(collection_path.split('/')[-1])
        if collection and collection.path != collection_path:
            raise DBusErrorNoSuchObject()
        return collection

    @debug_me
    def __init__(self, bus, pass_store):
        self.bus = bus
        self.pass_store = pass_store
        self.pub_ref = self.bus.publish(bus_name, self)
        self.collections = {}
        self.aliases = {}
        for collection_name in self.pass_store.get_collections():
            Collection(self, name=collection_name)
        self._set_aliases({ alias: self.collections.get(collection_name) for alias, collection_name in self.pass_store.get_aliases().items() })

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
        collection = Collection(self, properties=properties)
        if alias != '':
            self._set_aliases({ alias: collection })
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
        alias = self.aliases.get(name)
        return alias['collection'].path if alias else '/'

    @debug_me
    def SetAlias(self, name, collection):
        self._set_aliases({ name: self._get_collection_from_path(collection) })
        return None

    CollectionCreated = signal()
    CollectionDeleted = signal()
    CollectionChanged = signal()

    @property
    @debug_me
    def Collections(self):
        return [ collection.path for collection in self.collections.values() ]
