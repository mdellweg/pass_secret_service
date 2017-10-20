#!/usr/bin/env python3

import signal
import pydbus
from gi.repository import GLib
from interfaces.service import Service

def sigterm(mainloop):
    mainloop.quit()

if __name__ == '__main__':
    bus = pydbus.SessionBus()
    service = Service(bus)

    mainloop = GLib.MainLoop()
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM,
                         sigterm, mainloop)

    mainloop.run()
