#!/usr/bin/env python3

import asyncio
import click
import functools
import logging
import signal

from dbus_next.aio import MessageBus

from pass_secret_service.common.names import bus_name
from pass_secret_service.common.pass_store import PassStore
from pass_secret_service.interfaces.service import Service


logger = logging.getLogger()


def term_loop(loop):
    logger.info("Exiting...")
    loop.stop()


async def register_service(pass_store):
    bus = await MessageBus().connect()
    service = await Service._init(bus, pass_store)
    reply = await bus.request_name(bus_name)
    logger.info(repr(reply))
    # TODO check reply for PRIMARY_OWNER
    return service


def _main(path, verbose):
    if verbose:
        logging.basicConfig(level=20)
    pass_store = PassStore(**({'path': path} if path else {}))
    mainloop = asyncio.get_event_loop()
    mainloop.add_signal_handler(signal.SIGTERM, functools.partial(term_loop, mainloop))
    mainloop.add_signal_handler(signal.SIGINT, functools.partial(term_loop, mainloop))
    try:
        logger.info("Register Service")
        service = mainloop.run_until_complete(register_service(pass_store))
        logger.info("Running main loop")
        mainloop.run_forever()
    finally:
        mainloop.stop()
        mainloop.run_until_complete(service._unregister())
        mainloop.run_until_complete(mainloop.shutdown_asyncgens())
        mainloop.close()


@click.command()
@click.option('--path', help='path to the password store (optional)')
@click.option('-v', '--verbose', help='be verbose', is_flag=True, default=False)
def main(path, verbose):
    _main(path, verbose)


if __name__ == '__main__':  # pragma: no cover
    main()
