#!/usr/bin/env python3

import signal
import pydbus
from gi.repository import GLib
import click

from interfaces.service import Service
from common.pass_store import PassStore

def sigterm(mainloop):
    mainloop.quit()

@click.command()
@click.option('--path', help='path to the password store (optional)')
def main(path):
    bus = pydbus.SessionBus()
    pass_store = PassStore(**({'path': path} if path else {}) )
    service = Service(bus, pass_store)

    mainloop = GLib.MainLoop()
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM,
                         sigterm, mainloop)

    mainloop.run()

if __name__ == '__main__':  # pragma: no branch
    main()
