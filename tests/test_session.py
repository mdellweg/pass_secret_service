#!/usr/bin/env python3

import secretstorage

bus = secretstorage.dbus_init()

secretstorage.get_default_collection(bus)
