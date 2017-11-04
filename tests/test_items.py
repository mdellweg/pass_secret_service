#!/usr/bin/env python3

import unittest
import pydbus
from gi.repository import GLib
from common.names import bus_name, base_path

class TestCollection(unittest.TestCase):
    def setUp(self):
        self.bus = pydbus.SessionBus()
        self.service = self.bus.get(bus_name)
        self.default_collection = self.bus.get(bus_name, '/org/freedesktop/secrets/aliases/default')
        dummy, self.session_path = self.service.OpenSession('plain', GLib.Variant('s', ''))

    def tearDown(self):
        self.bus.get(bus_name, self.session_path).Close()

    def test_create_delete_item(self):
        item_path, prompt_path = self.default_collection.CreateItem({}, (self.session_path, b'', b'password', 'text/plain'), False)
        item = self.bus.get(bus_name, item_path)
        self.assertIn(item_path, self.default_collection.Items)
        self.assertEqual((self.session_path, list(b''),list(b'password'), 'text/plain'), item.GetSecret(self.session_path))
        item.SetSecret((self.session_path, b'', b'secret', 'text/plain'))
        self.assertEqual((self.session_path, list(b''),list(b'secret'), 'text/plain'), item.GetSecret(self.session_path))
        item.Delete()
        self.assertNotIn(item_path, self.default_collection.Items)

    def test_get_and_set_secret(self):
        item_path, prompt_path = self.default_collection.CreateItem({}, (self.session_path, b'', b'password', 'text/plain'), False)
        item = self.bus.get(bus_name, item_path)
        self.assertEqual((self.session_path, list(b''),list(b'password'), 'text/plain'), item.GetSecret(self.session_path))
        item.SetSecret((self.session_path, b'', b'secret', 'text/plain'))
        self.assertEqual((self.session_path, list(b''),list(b'secret'), 'text/plain'), item.GetSecret(self.session_path))
        item.Delete()

    def test_item_properties(self):
        properties = {
            'org.freedesktop.Secret.Item.Label': GLib.Variant('s', 'test_label'),
            'org.freedesktop.Secret.Item.Attributes': GLib.Variant('a{ss}', {'attr1': 'val1'}),
        }
        item_path, prompt_path = self.default_collection.CreateItem(properties, (self.session_path, b'', b'password', 'text/plain'), False)
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

    def test_items_property(self):
        self.assertIn('/org/freedesktop/secrets/collection/default/aaaa', self.default_collection.Items)

    def test_broken_session_path(self):
        with self.assertRaises(GLib.GError) as context:
            item_path, prompt_path = self.default_collection.CreateItem({}, (self.session_path + 'tilt', b'', b'password', 'text/plain'), False)
        self.assertIn('NoSession', str(context.exception))

        with self.assertRaises(GLib.GError) as context:
            item_path, prompt_path = self.default_collection.CreateItem({}, ('/tilt' + self.session_path, b'', b'password', 'text/plain'), False)
        self.assertIn('NoSuchObject', str(context.exception))

if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
