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
        collection_path, prompt_path = self.service.CreateCollection({'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', 'test_collection_label')}, 'test_alias')
        collection = self.bus.get(bus_name, collection_path)
        self.assertEqual(collection.Label, 'test_collection_label')
        self.assertIn(collection_path, self.service.Collections)
        self.assertEqual(collection_path, self.service.ReadAlias('test_alias'))
        collection.Delete()
        self.assertNotIn(collection_path, self.service.Collections)

    def test_properties(self):
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        collection.Label
        collection.Locked
        collection.Created
        collection.Modified

if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
