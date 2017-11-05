#!/usr/bin/env python3

import unittest
import pydbus
from gi.repository import GLib
from common.names import bus_name, base_path

class TestService(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()
        self.service = self.bus.get(bus_name)

    def test_collections_property(self):
        self.assertIn('/org/freedesktop/secrets/collection/default', self.service.Collections)

    def test_get_default_collection(self):
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')

    def test_read_alias(self):
        self.assertEqual('/org/freedesktop/secrets/collection/default', self.service.ReadAlias('default'))
        self.assertEqual('/', self.service.ReadAlias('defect'))

    def test_set_alias(self):
        ALIAS = 'aabb'
        TRACER = 'ccdd'
        collection_path1, prompt_path = self.service.CreateCollection({}, '')
        collection_path2, prompt_path = self.service.CreateCollection({'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', TRACER)}, '')
        collection1 = self.bus.get(bus_name, collection_path1)
        collection2 = self.bus.get(bus_name, collection_path2)
        self.service.SetAlias(ALIAS, collection_path1)
        self.service.SetAlias(ALIAS, collection_path2)
        self.service.SetAlias(ALIAS, collection_path2)
        self.assertEqual(collection_path2, self.service.ReadAlias(ALIAS))
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/' + ALIAS)
        self.assertEqual(TRACER, collection.Label)
        collection1.Delete()
        self.assertEqual(collection_path2, self.service.ReadAlias(ALIAS))
        collection2.Delete()
        self.assertEqual('/', self.service.ReadAlias(ALIAS))

    def test_get_secrets(self):
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        prompt_path, session_path = self.service.OpenSession('plain', GLib.Variant('s', ''))
        item1_path, prompt_path = collection.CreateItem({}, (session_path, b'', b'password1', 'text/plain'), False)
        item2_path, prompt_path = collection.CreateItem({}, (session_path, b'', b'password2', 'text/plain'), False)
        secrets = self.service.GetSecrets([item1_path, item2_path], session_path)
        self.assertEqual(2, len(secrets))
        self.assertEqual(list(b'password1'), secrets[item1_path][2])
        self.assertEqual(list(b'password2'), secrets[item2_path][2])

if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
