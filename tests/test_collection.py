#!/usr/bin/env python3

import unittest
from tests.helper import with_service
import pydbus
from gi.repository import GLib
from common.names import bus_name, base_path

class TestCollection(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()

    @with_service
    def test_create_delete_collection(self):
        service = self.bus.get(bus_name)
        collection_path, prompt_path = service.CreateCollection({'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', 'test_collection_label')}, 'test_alias')
        collection = self.bus.get(bus_name, collection_path)
        self.assertEqual(collection.Label, 'test_collection_label')
        self.assertIn(collection_path, service.Collections)
        self.assertEqual(collection_path, service.ReadAlias('test_alias'))
        collection.Delete()
        self.assertNotIn(collection_path, service.Collections)

    @with_service
    def test_properties(self):
        service = self.bus.get(bus_name)
        collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        collection.Label
        collection.Locked
        collection.Created
        collection.Modified

    @with_service
    def test_lock_unlock(self):
        service = self.bus.get(bus_name)
        collection_path, prompt_path = service.CreateCollection({'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', 'test_lock_label')}, '')
        collection = self.bus.get(bus_name, collection_path)
        service.Lock([collection_path])
        self.assertTrue(collection.Locked)
        service.Unlock([collection_path])
        self.assertFalse(collection.Locked)

if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
