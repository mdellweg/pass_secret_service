#!/usr/bin/env python3

import unittest
from test.helper import ServiceEnv, with_service
import pydbus
from gi.repository import GLib

from pass_secret_service.common.names import bus_name, base_path


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()

    @with_service
    def test_create_delete_collection(self):
        service = self.bus.get(bus_name)
        properties = {'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', 'test_collection_label')}
        collection_path, prompt_path = service.CreateCollection(properties, 'test_alias')
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
        properties = {'org.freedesktop.Secret.Collection.Label': GLib.Variant('s', 'test_lock_label')}
        collection_path, prompt_path = service.CreateCollection(properties, '')
        collection = self.bus.get(bus_name, collection_path)
        service.Lock([collection_path])
        self.assertTrue(collection.Locked)
        service.Unlock([collection_path])
        self.assertFalse(collection.Locked)

    def test_persisted_item(self):
        with ServiceEnv():
            service = self.bus.get(bus_name)
            default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
            dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
            default_collection.CreateItem({}, (session_path, b'', b'password', 'text/plain'), True)
        with ServiceEnv(clean=False):
            service = self.bus.get(bus_name)
            default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
            self.assertEqual(1, len(default_collection.Items))


if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
