# Implementation of the org.freedesktop.Secret.Service interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib

from pass_secret_service.common.debug import debug_me
from pass_secret_service.common.exceptions import DBusErrorNotSupported, DBusErrorNoSuchObject, DBusErrorNoSession
from pass_secret_service.common.names import bus_name, base_path, COLLECTION_LABEL
from pass_secret_service.interfaces.collection import Collection
from pass_secret_service.interfaces.session import Session


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

    # finder
    @staticmethod
    def _get_relative_object_path(object_path):
        if object_path.startswith('/org/freedesktop/secrets/'):
            return object_path[25:]
        else:
            raise DBusErrorNoSuchObject()

    def _get_collection_from_path(self, collection_path):
        if collection_path == '/':
            return None
        collection = None
        path_components = self._get_relative_object_path(collection_path).split('/')
        if len(path_components) == 2:
            if path_components[0] == 'collection':
                collection = self.collections.get(path_components[1])
            elif path_components[0] == 'aliases':
                collection = self.aliases.get(path_components[1], {'collection': None})['collection']
        if collection is None:
            raise DBusErrorNoSuchObject()
        return collection

    def _get_item_from_path(self, item_path):
        if item_path == '/':
            return None
        path_components = self._get_relative_object_path(item_path).split('/')
        if len(path_components) != 3 or path_components[0] != 'collection':
            raise DBusErrorNoSuchObject()
        collection = self.collections.get(path_components[1])
        if collection is None:
            raise DBusErrorNoSuchObject()
        item = collection.items.get(path_components[2])
        if item is None:
            raise DBusErrorNoSuchObject()
        return item

    def _get_session_from_path(self, session_path):
        path_components = self._get_relative_object_path(session_path).split('/')
        if len(path_components) != 2 or path_components[0] != 'session':
            raise DBusErrorNoSuchObject()
        session = self.sessions.get(path_components[1])
        if session is None:
            raise DBusErrorNoSession()
        return session

    # Alias helpers
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
            self.aliases[alias] = {'collection': collection, 'pub_ref': alias_ref}
            changed = True
        return changed

    def _set_aliases(self, alias_dict):
        changed = False
        for alias, collection in alias_dict.items():
            if self._set_alias(alias, collection):
                changed = True
        if changed:
            self.pass_store.save_aliases({key: value['collection'].name for key, value in self.aliases.items()})

    # secret helper
    def _encode_secret(self, session_path, password):
        session = self._get_session_from_path(session_path)
        return session._encode_secret(password)

    def _decode_secret(self, secret):
        session = self._get_session_from_path(secret[0])
        return session._decode_secret(secret)

    def _unregister(self):
        for session in self.sessions.values():
            session._unregister()
        for alias in self.aliases.values():
            alias['pub_ref'].unregister()
        for collection in self.collections.values():
            collection._unregister()
        self.pub_ref.unpublish()

    @debug_me
    def __init__(self, bus, pass_store):
        self.bus = bus
        self.pass_store = pass_store
        self.sessions = {}
        self.collections = {}
        self.aliases = {}
        for collection_name in self.pass_store.get_collections():
            Collection(self, collection_name)
        self._set_aliases({alias: self.collections.get(collection_name) for alias, collection_name in self.pass_store.get_aliases().items()})
        # Create default collection if need be
        if 'default' not in self.aliases:
            self.CreateCollection({COLLECTION_LABEL: 'default collection'}, 'default')
        # Register with dbus
        self.pub_ref = self.bus.publish(bus_name, self)

    @debug_me
    def OpenSession(self, algorithm, input):
        if algorithm == 'plain':
            output = GLib.Variant('s', '')
            new_session = Session._create_plain(self)
            result = new_session.path
            return output, result
        if algorithm == 'dh-ietf1024-sha256-aes128-cbc-pkcs7':
            new_session, output = Session._create_dh(self, input)
            result = new_session.path
            return output, result
        raise DBusErrorNotSupported('algorithm "{}" is not implemented'.format(algorithm))

    @debug_me
    def CreateCollection(self, properties, alias):
        collection = Collection._create(self, properties)
        if alias != '':
            self._set_aliases({alias: collection})
        prompt = '/'
        return collection.path, prompt

    @debug_me
    def SearchItems(self, attributes):
        unlocked = []
        locked = []
        for collection in self.collections.values():
            if collection.Locked:
                locked.extend(collection.SearchItems(attributes))
            else:
                unlocked.extend(collection.SearchItems(attributes))
        return unlocked, locked

    @debug_me
    def Unlock(self, objects):
        unlocked = []
        for obj_path in objects:
            try:
                collection = self._get_collection_from_path(obj_path)
                if collection:
                    collection._unlock()
                    unlocked.append(obj_path)
                    continue
            except DBusErrorNoSuchObject:
                pass
            try:
                item = self._get_item_from_path(obj_path)
                if item:
                    item.collection._unlock()
                    unlocked.append(obj_path)
                    continue
            except DBusErrorNoSuchObject:
                pass
        prompt = '/'
        return unlocked, prompt

    @debug_me
    def Lock(self, objects):
        locked = []
        for obj_path in objects:
            try:
                collection = self._get_collection_from_path(obj_path)
                if collection:
                    collection._lock()
                    locked.append(obj_path)
                    continue
            except DBusErrorNoSuchObject:
                pass
        prompt = '/'
        return locked, prompt

    @debug_me
    def GetSecrets(self, items, session):
        secrets = {}
        session = self._get_session_from_path(session)
        for item_path in items:
            item = self._get_item_from_path(item_path)
            password = item._get_password()
            secrets[item_path] = session._encode_secret(password)
        return secrets

    @debug_me
    def ReadAlias(self, name):
        alias = self.aliases.get(name)
        return alias['collection'].path if alias else '/'

    @debug_me
    def SetAlias(self, name, collection):
        self._set_aliases({name: self._get_collection_from_path(collection)})

    CollectionCreated = signal()
    CollectionDeleted = signal()
    CollectionChanged = signal()

    @property
    @debug_me
    def Collections(self):
        return [collection.path for collection in self.collections.values()]

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
