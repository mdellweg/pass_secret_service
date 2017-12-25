#!/usr/bin/env python3

import unittest
from test.helper import with_service
import pydbus
from gi.repository import GLib

from pass_secret_service.common.names import bus_name, base_path


class TestService(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()

    @with_service
    def test_collections_property(self):
        service = self.bus.get(bus_name)
        self.assertIn(service.ReadAlias('default'), service.Collections)

    @with_service
    def test_get_default_collection(self):
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        self.assertEqual('default collection', collection.Label)

    @with_service
    def test_read_alias(self):
        service = self.bus.get(bus_name)
        self.assertRegex(service.ReadAlias('default'), '/org/freedesktop/secrets/collection/.*')
        self.assertEqual('/', service.ReadAlias('defect'))

    @with_service
    def test_set_alias(self):
        service = self.bus.get(bus_name)
        ALIAS = 'aabb'
        TRACER = 'ccdd'
        collection_path1, prompt_path = service.CreateCollection({}, '')
        collection_path2, prompt_path = service.CreateCollection({'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', TRACER)}, '')
        collection1 = self.bus.get(bus_name, collection_path1)
        collection2 = self.bus.get(bus_name, collection_path2)
        service.SetAlias(ALIAS, collection_path1)
        self.assertEqual(collection_path1, service.ReadAlias(ALIAS))
        service.SetAlias(ALIAS, '/')
        self.assertEqual('/', service.ReadAlias(ALIAS))
        service.SetAlias(ALIAS, collection_path1)
        service.SetAlias(ALIAS, collection_path2)
        service.SetAlias(ALIAS, collection_path2)
        self.assertEqual(collection_path2, service.ReadAlias(ALIAS))
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/' + ALIAS)
        self.assertEqual(TRACER, collection.Label)
        collection1.Delete()
        self.assertEqual(collection_path2, service.ReadAlias(ALIAS))
        collection2.Delete()
        self.assertEqual('/', service.ReadAlias(ALIAS))

    @with_service
    def test_get_secrets(self):
        service = self.bus.get(bus_name)
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        prompt_path, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        item1_path, prompt_path = collection.CreateItem({}, (session_path, b'', b'password1', 'text/plain'), False)
        item2_path, prompt_path = collection.CreateItem({}, (session_path, b'', b'password2', 'text/plain'), False)
        secrets = service.GetSecrets([item1_path, item2_path], session_path)
        self.assertEqual(2, len(secrets))
        self.assertEqual(list(b'password1'), secrets[item1_path][2])
        self.assertEqual(list(b'password2'), secrets[item2_path][2])

    @with_service
    def test_lock_unlock_collection(self):
        service = self.bus.get(bus_name)
        locked, dummy = service.Lock(['/org/freedesktop/secrets/aliases/default', '/org/freedesktop/secrets/aliases/nodefault', '/'])
        self.assertIn('/org/freedesktop/secrets/aliases/default', locked)
        self.assertNotIn('/org/freedesktop/secrets/aliases/nodefault', locked)
        self.assertNotIn('/', locked)
        unlocked, dummy = service.Unlock(['/org/freedesktop/secrets/aliases/default', '/org/freedesktop/secrets/aliases/nodefault', '/'])
        self.assertIn('/org/freedesktop/secrets/aliases/default', unlocked)
        self.assertNotIn('/org/freedesktop/secrets/aliases/nodefault', unlocked)
        self.assertNotIn('/', unlocked)
        unlocked, dummy = service.Unlock(['/org/freedesktop/secrets/collection/nodefault/test', service.ReadAlias('default') + '/test'])
        self.assertEqual([], unlocked)
        unlocked, dummy = service.Unlock(['/org/freedesktop/secrets/nocollection/default'])
        self.assertEqual([], unlocked)

    @with_service
    def test_empty_session(self):
        service = self.bus.get(bus_name)
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        with self.assertRaises(GLib.GError):
            item1_path, prompt_path = collection.CreateItem({}, ('/', b'', b'password1', 'text/plain'), False)
        with self.assertRaises(GLib.GError):
            item1_path, prompt_path = collection.CreateItem({}, ('/org/freedesktop/secrets/nosession/test', b'', b'password1', 'text/plain'), False)


if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
