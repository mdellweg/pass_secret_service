#!/usr/bin/env python3

import unittest
import pydbus
from gi.repository import GLib
from common.names import bus_name, base_path

class TestCollection(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()
        self.service = self.bus.get(bus_name)

    def test_create_delete_collection(self):
        collection_path, prompt_path = self.service.CreateCollection({'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', 'test_label')}, 'test_alias')
        collection = self.bus.get(bus_name, collection_path)
        self.assertEqual(collection.Label, 'test_label')
        self.assertIn(collection_path, self.service.Collections)
        self.assertEqual(collection_path, self.service.ReadAlias('test_alias'))
        collection.Delete()
        self.assertNotIn(collection_path, self.service.Collections)

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

if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
