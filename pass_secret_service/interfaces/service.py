# Implementation of the org.freedesktop.Secret.Service interface

from dbus_next.service import (
    dbus_property,
    method,
    PropertyAccess,
    ServiceInterface,
    signal,
)
from dbus_next import Variant

from pass_secret_service.common.exceptions import (
    DBusErrorNotSupported,
    DBusErrorNoSuchObject,
    DBusErrorNoSession,
)
from pass_secret_service.common.names import base_path, COLLECTION_LABEL
from pass_secret_service.interfaces.collection import Collection
from pass_secret_service.interfaces.session import Session


class Service(ServiceInterface):

    # finder
    @staticmethod
    def _get_relative_object_path(object_path):
        if object_path.startswith('/org/freedesktop/secrets/'):
            return object_path[25:]
        else:
            raise DBusErrorNoSuchObject(object_path)

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
            raise DBusErrorNoSuchObject(collection_path)
        return collection

    def _get_item_from_path(self, item_path):
        if item_path == '/':
            return None
        path_components = self._get_relative_object_path(item_path).split('/')
        if len(path_components) != 3 or path_components[0] != 'collection':
            raise DBusErrorNoSuchObject(item_path)
        collection = self.collections.get(path_components[1])
        if collection is None:
            raise DBusErrorNoSuchObject(item_path)
        item = collection.items.get(path_components[2])
        if item is None:
            raise DBusErrorNoSuchObject(item_path)
        return item

    def _get_session_from_path(self, session_path):
        path_components = self._get_relative_object_path(session_path).split('/')
        if len(path_components) != 2 or path_components[0] != 'session':
            raise DBusErrorNoSuchObject(session_path)
        session = self.sessions.get(path_components[1])
        if session is None:
            raise DBusErrorNoSession(session_path)
        return session

    # Alias helpers
    def _set_alias(self, alias, collection):
        changed = False
        old_alias = self.aliases.get(alias)
        if old_alias:
            if old_alias['collection'] == collection:
                return changed
            self.bus.unexport(old_alias['path'])
            self.aliases.pop(alias)
            changed = True
        if collection:
            alias_path = base_path + '/aliases/' + alias
            self.bus.export(alias_path, collection)
            self.aliases[alias] = {'collection': collection, 'path': alias_path}
            changed = True
        return changed

    def _set_aliases(self, alias_dict):
        changed = False
        for alias, collection in alias_dict.items():
            if self._set_alias(alias, collection):
                changed = True
        if changed:
            self.pass_store.save_aliases({key: value['collection'].id for key, value in self.aliases.items()})

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
            self.bus.unexport(alias['path'])
        for collection in self.collections.values():
            collection._unregister()
        self.bus.unexport(self.path)

    def __init__(self, bus, pass_store):
        super().__init__('org.freedesktop.Secret.Service')
        self.bus = bus
        self.pass_store = pass_store
        self.sessions = {}
        self.collections = {}
        self.aliases = {}
        self.path = base_path
        for collection_id in self.pass_store.get_collections():
            Collection(self, collection_id)
        self._set_aliases({alias: self.collections.get(collection_id) for alias, collection_id in self.pass_store.get_aliases().items()})
        # Create default collection if need be
        if 'default' not in self.aliases:
            self.CreateCollection({COLLECTION_LABEL: Variant('s', 'default collection')}, 'default')
        self.bus.export(self.path, self)

    @method()
    def OpenSession(self, algorithm: 's', input: 'v') -> 'vo':
        if algorithm == 'plain':
            output = Variant('s', '')
            new_session = Session._create_plain(self)
            result = new_session.path
            return [output, result]
        if algorithm == 'dh-ietf1024-sha256-aes128-cbc-pkcs7':
            new_session, output = Session._create_dh(self, input.value)
            result = new_session.path
            return [output, result]
        raise DBusErrorNotSupported('algorithm "{}" is not implemented'.format(algorithm))

    @method()
    def CreateCollection(self, properties: 'a{sv}', alias: 's') -> 'oo':
        collection = Collection._create(self, {k: v.value for k, v in properties.items()})
        if alias != '':
            self._set_aliases({alias: collection})
        prompt = '/'
        return [collection.path, prompt]

    @method()
    def SearchItems(self, attributes: 'a{ss}') -> 'aoao':
        unlocked = []
        locked = []
        for collection in self.collections.values():
            if collection.locked:
                locked.extend(collection._search_items(attributes))
            else:
                unlocked.extend(collection._search_items(attributes))
        return [unlocked, locked]

    @method()
    def Unlock(self, objects: 'ao') -> 'aoo':
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
        return [unlocked, prompt]

    @method()
    def Lock(self, objects: 'ao') -> 'aoo':
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
        return [locked, prompt]

    @method()
    def GetSecrets(self, items: 'ao', session: 'o') -> 'a{o(oayays)}':
        secrets = {}
        session = self._get_session_from_path(session)
        for item_path in items:
            item = self._get_item_from_path(item_path)
            password = item._get_password()
            secrets[item_path] = session._encode_secret(password)
        return secrets

    @method()
    def ReadAlias(self, name: 's') -> 'o':
        alias = self.aliases.get(name)
        return alias['collection'].path if alias else '/'

    @method()
    def SetAlias(self, name: 's', collection: 'o') -> '':
        self._set_aliases({name: self._get_collection_from_path(collection)})

    @signal()
    def CollectionCreated(self, collection) -> 'o':
        return collection.path

    @signal()
    def CollectionDeleted(self, collection) -> 'o':
        return collection.path

    @signal()
    def CollectionChanged(self, collection) -> 'o':
        return collection.path

    @dbus_property(access=PropertyAccess.READ)
    def Collections(self) -> 'ao':
        return [collection.path for collection in self.collections.values()]

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
