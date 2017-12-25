#!/usr/bin/env python3

import unittest
from test.helper import with_service
import pydbus
from gi.repository import GLib

from pass_secret_service.common.names import bus_name, base_path


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()

    @with_service
    def test_create_delete_item(self):
        service = self.bus.get(bus_name)
        default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        item_path, prompt_path = default_collection.CreateItem({}, (session_path, b'', b'password', 'text/plain'), False)
        item = self.bus.get(bus_name, item_path)
        self.assertIn(item_path, default_collection.Items)
        self.assertEqual((session_path, list(b''), list(b'password'), 'text/plain'), item.GetSecret(session_path))
        item.SetSecret((session_path, b'', b'secret', 'text/plain'))
        self.assertEqual((session_path, list(b''), list(b'secret'), 'text/plain'), item.GetSecret(session_path))
        item.Delete()
        self.assertNotIn(item_path, default_collection.Items)
        self.bus.get(bus_name, session_path).Close()

    @with_service
    def test_get_and_set_secret(self):
        service = self.bus.get(bus_name)
        default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        item_path, prompt_path = default_collection.CreateItem({}, (session_path, b'', b'password', 'text/plain'), False)
        item = self.bus.get(bus_name, item_path)
        self.assertEqual((session_path, list(b''), list(b'password'), 'text/plain'), item.GetSecret(session_path))
        item.SetSecret((session_path, b'', b'secret', 'text/plain'))
        self.assertEqual((session_path, list(b''), list(b'secret'), 'text/plain'), item.GetSecret(session_path))
        item.Delete()
        self.bus.get(bus_name, session_path).Close()

    @with_service
    def test_item_properties(self):
        service = self.bus.get(bus_name)
        default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        properties = {
            'org.freedesktop.Secret.Item.Label': GLib.Variant('s', 'test_label'),
            'org.freedesktop.Secret.Item.Attributes': GLib.Variant('a{ss}', {'attr1': 'val1'}),
        }
        item_path, prompt_path = default_collection.CreateItem(properties, (session_path, b'', b'password', 'text/plain'), False)
        item = self.bus.get(bus_name, item_path)
        self.assertEqual(item.Label, 'test_label')
        item.Label = 'test_label2'
        item.Label = 'test_label2'
        self.assertEqual(item.Label, 'test_label2')
        self.assertEqual(item.Attributes, {'attr1': 'val1'})
        item.Attributes = {'attr1': 'val2'}
        item.Attributes = {'attr1': 'val2'}
        self.assertEqual(item.Attributes, {'attr1': 'val2'})
        self.assertEqual(item.Locked, False)
        self.assertEqual(item.Created, 0)
        self.assertEqual(item.Modified, 0)
        item.Delete()
        self.bus.get(bus_name, session_path).Close()

    @with_service
    def test_broken_session_path(self):
        service = self.bus.get(bus_name)
        default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        with self.assertRaises(GLib.GError) as context:
            item_path, prompt_path = default_collection.CreateItem({}, (session_path + 'tilt', b'', b'password', 'text/plain'), False)
        self.assertIn('NoSession', str(context.exception))

        with self.assertRaises(GLib.GError) as context:
            item_path, prompt_path = default_collection.CreateItem({}, ('/tilt' + session_path, b'', b'password', 'text/plain'), False)
        self.assertIn('NoSuchObject', str(context.exception))
        self.bus.get(bus_name, session_path).Close()

    @with_service
    def test_item_lookup(self):
        service = self.bus.get(bus_name)
        default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        attributes = {'lookup_attr1': '1', 'lookup_attr2': '2'}
        properties = {
            'org.freedesktop.Secret.Item.Label': GLib.Variant('s', 'lookup_label1'),
            'org.freedesktop.Secret.Item.Attributes': GLib.Variant('a{ss}', attributes),
        }
        item_path, prompt_path = default_collection.CreateItem(properties, (session_path, b'', b'password', 'text/plain'), False)
        self.assertIn(item_path, service.SearchItems({'lookup_attr1': '1'})[0])
        self.assertIn(item_path, service.SearchItems({'lookup_attr1': '1', 'lookup_attr2': '2'})[0])
        self.assertNotIn(item_path, service.SearchItems({'lookup_attr1': '1', 'lookup_attr2': '0'})[0])
        self.assertNotIn(item_path, service.SearchItems({'lookup_attr1': '1', 'lookup_attr3': '3'})[0])
        self.bus.get(bus_name, session_path).Close()

    @with_service
    def test_item_in_deleted_collection(self):
        service = self.bus.get(bus_name)
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        collection_path, promt_path = service.CreateCollection({}, 'delete_alias')
        collection = self.bus.get(bus_name, collection_path)
        properties = {
            'org.freedesktop.Secret.Item.Label': GLib.Variant('s', 'delete_label1'),
        }
        item_path, prompt_path = collection.CreateItem(properties, (session_path, b'', b'password', 'text/plain'), False)
        self.assertIn(item_path, service.SearchItems({})[0])
        collection.Delete()
        self.assertNotIn(item_path, service.SearchItems({})[0])
        self.bus.get(bus_name, session_path).Close()

    @with_service
    def test_replace_item(self):
        service = self.bus.get(bus_name)
        default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
        properties = {
            'org.freedesktop.Secret.Item.Label': GLib.Variant('s', 'test_label'),
            'org.freedesktop.Secret.Item.Attributes': GLib.Variant('a{ss}', {'lookup_attr': 'replace_test'}),
        }
        item1_path, prompt_path = default_collection.CreateItem(properties, (session_path, b'', b'password', 'text/plain'), True)
        item2_path, prompt_path = default_collection.CreateItem(properties, (session_path, b'', b'password', 'text/plain'), True)
        self.assertEqual(item1_path, item2_path)
        self.bus.get(bus_name, session_path).Close()


if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
