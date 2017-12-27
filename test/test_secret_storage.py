#!/usr/bin/env python3

# Run (integration) tests with external library secretstorage

import unittest
from test.helper import with_service
import secretstorage


class TestSecretStorage(unittest.TestCase):
    def setUp(self):
        self.bus = secretstorage.dbus_init()

    @with_service
    def test_default_collection(self):
        collection = secretstorage.get_default_collection(self.bus)
        collection.set_label('default')
        collection.set_label('default')
        collection.set_label('default1')
        self.assertEqual('default1', collection.get_label())

    @with_service
    def test_search_item(self):
        collection = secretstorage.get_default_collection(self.bus)
        collection.create_item('label1', {'attr1': 'val1', 'attr2': 'val2'}, 'secret passphrase')
        collection.create_item('label2', {'attr1': 'val1_tilt', 'attr2': 'val2'}, 'secret passphrase')
        collection.create_item('label3', {'attr1_tilt': 'val1', 'attr2': 'val2'}, 'secret passphrase')
        item_iter = secretstorage.search_items(self.bus, {'attr1': 'val1'})
        items = [i for i in item_iter]
        labels = [i.get_label() for i in items]
        item_iter = collection.search_items({'attr1': 'val1'})
        coll_labels = [i.get_label() for i in item_iter]
        self.assertEqual(labels, coll_labels)
        self.assertIn('label1', labels)
        self.assertNotIn('label2', labels)
        self.assertNotIn('label3', labels)
        self.assertEqual(b'secret passphrase', items[0].get_secret())


if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
