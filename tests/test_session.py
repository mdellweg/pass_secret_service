#!/usr/bin/env python3

import unittest
import secretstorage

class TestSession(unittest.TestCase):
    def setUp(self):
        self.bus = secretstorage.dbus_init()

    def test_default_collection(self):
        secretstorage.get_default_collection(self.bus)

if __name__ == "__main__":
    unittest.main()
