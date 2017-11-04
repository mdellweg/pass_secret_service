#!/usr/bin/env python3

# Run (integration) tests with external library secretstorage

import unittest
import secretstorage

class TestSecretStorage(unittest.TestCase):
    def setUp(self):
        self.bus = secretstorage.dbus_init()

    def test_default_collection(self):
        collection = secretstorage.get_default_collection(self.bus)
        collection.set_label('default')
        collection.set_label('default')
        collection.set_label('default1')
        self.assertEqual('default1', collection.get_label())

    def test_search_item(self):
        secretstorage.search_items(self.bus, {})

if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
