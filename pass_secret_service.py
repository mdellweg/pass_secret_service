#!/usr/bin/env python3

import subprocess
import pydbus
from gi.repository import GLib
from interfaces.service import Service

if __name__ == '__main__':
    bus = pydbus.SessionBus()
    Service(bus)

    loop = GLib.MainLoop()
    loop.run()
