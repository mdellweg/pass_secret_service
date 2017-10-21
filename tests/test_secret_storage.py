#!/usr/bin/env python3

# Run (integration) tests with external library secretstorage

import unittest
import secretstorage

class TestSecretStorage(unittest.TestCase):
    def setUp(self):
        self.bus = secretstorage.dbus_init()

    def test_default_collection(self):
        collection = secretstorage.get_default_collection(self.bus)

if __name__ == "__main__":
    unittest.main()
