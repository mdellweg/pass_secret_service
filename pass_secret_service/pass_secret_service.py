#!/usr/bin/env python3

import signal
import pydbus
from gi.repository import GLib
import click

from pass_secret_service.interfaces.service import Service
from pass_secret_service.common.pass_store import PassStore


def sigterm(mainloop):
    mainloop.quit()


@click.command()
@click.option('--path', help='path to the password store (optional)')
def main(path):
    bus = pydbus.SessionBus()
    pass_store = PassStore(**({'path': path} if path else {}))
    service = Service(bus, pass_store)
    mainloop = GLib.MainLoop()
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, sigterm, mainloop)
    mainloop.run()
    service._unregister()


if __name__ == '__main__':  # pragma: no cover
    main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
