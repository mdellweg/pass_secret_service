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
from pass_secret_service.common.tools import run_in_executor
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

    @run_in_executor
    def _save_aliases(self):
        self.pass_store.save_aliases({key: value['collection'].id for key, value in self.aliases.items()})

    async def _set_aliases(self, alias_dict):
        changed = False
        for alias, collection in alias_dict.items():
            if self._set_alias(alias, collection):
                changed = True
        if changed:
            await self._save_aliases()

    # secret helper
    async def _encode_secret(self, session_path, password):
        session = self._get_session_from_path(session_path)
        return await session._encode_secret(password)

    async def _decode_secret(self, secret):
        session = self._get_session_from_path(secret[0])
        return await session._decode_secret(secret)

    async def _unregister(self):
        for session in self.sessions.values():
            await session._unregister()
        for alias in self.aliases.values():
            self.bus.unexport(alias['path'])
        for collection in self.collections.values():
            await collection._unregister()
        self.bus.unexport(self.path)

    def __init__(self, bus, pass_store):
        super().__init__('org.freedesktop.Secret.Service')
        self.bus = bus
        self.pass_store = pass_store
        self.sessions = {}
        self.collections = {}
        self.aliases = {}
        self.path = base_path

    @run_in_executor
    def _get_collections(self):
        return self.pass_store.get_collections()

    @run_in_executor
    def _get_aliases(self):
        return self.pass_store.get_aliases()

    @classmethod
    async def _init(cls, bus, pass_store):
        self = cls(bus, pass_store)
        for collection_id in await self._get_collections():
            await Collection._init(self, collection_id)
        aliases = await self._get_aliases()
        await self._set_aliases({alias: self.collections.get(collection_id) for alias, collection_id in aliases.items()})
        # Create default collection if need be
        if 'default' not in self.aliases:
            await self._create_collection({COLLECTION_LABEL: Variant('s', 'default collection')}, 'default')
        # Register with dbus
        self.bus.export(self.path, self)
        return self

    @method()
    async def OpenSession(self, algorithm: 's', input: 'v') -> 'vo':
        if algorithm == 'plain':
            aes_key = None
            output = Variant('s', '')
        elif algorithm == 'dh-ietf1024-sha256-aes128-cbc-pkcs7':
            aes_key, output = await Session._create_dh(input.value)
        else:
            raise DBusErrorNotSupported('algorithm "{}" is not implemented'.format(algorithm))
        new_session = Session(self, aes_key=aes_key)
        result = new_session.path
        return [output, result]

    async def _create_collection(self, properties, alias):
        collection = await Collection._create(self, {k: v.value for k, v in properties.items()})
        if alias != '':
            await self._set_aliases({alias: collection})
        return collection

    @method()
    async def CreateCollection(self, properties: 'a{sv}', alias: 's') -> 'oo':
        collection = await self._create_collection(properties, alias)
        prompt = '/'
        return [collection.path, prompt]

    @method()
    async def SearchItems(self, attributes: 'a{ss}') -> 'aoao':
        unlocked = []
        locked = []
        for collection in self.collections.values():
            if collection.locked:
                locked.extend(collection._search_items(attributes))
            else:
                unlocked.extend(collection._search_items(attributes))
        return [unlocked, locked]

    @method()
    async def Unlock(self, objects: 'ao') -> 'aoo':
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
    async def Lock(self, objects: 'ao') -> 'aoo':
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
    async def GetSecrets(self, items: 'ao', session: 'o') -> 'a{o(oayays)}':
        secrets = {}
        session = self._get_session_from_path(session)
        for item_path in items:
            item = self._get_item_from_path(item_path)
            password = await item._get_password()
            secrets[item_path] = await session._encode_secret(password)
        return secrets

    @method()
    async def ReadAlias(self, name: 's') -> 'o':
        alias = self.aliases.get(name)
        return alias['collection'].path if alias else '/'

    @method()
    async def SetAlias(self, name: 's', collection: 'o') -> '':
        await self._set_aliases({name: self._get_collection_from_path(collection)})

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
