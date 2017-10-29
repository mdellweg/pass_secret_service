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
        collection.Delete()
        self.assertNotIn(collection_path, self.service.Collections)

    def test_collections_property(self):
        self.assertIn('/org/freedesktop/secrets/collection/default', self.service.Collections)

    def not_yet_test_get_default_collection(self):
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')

if __name__ == "__main__":
    unittest.main()
