# Run (integration) tests with external library secretstorage

import asyncio
import pytest
import threading
import secretstorage
import time

from .helper import ServiceEnv


async def run_service(started_cond, shutdown_cond):
    async with ServiceEnv():
        with started_cond:
            started_cond.notify_all()
        async with shutdown_cond:
            await shutdown_cond.wait()


async def shutdown_service(shutdown_cond):
    async with shutdown_cond:
        shutdown_cond.notify_all()


async def create_cond():
    return asyncio.Condition()


def loop_thread(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        loop.close()


@pytest.fixture(autouse=True)
def secret_service():
    loop = asyncio.new_event_loop()
    started_cond = threading.Condition()
    thread = threading.Thread(target=loop_thread, args=(loop, ), daemon=True)
    thread.start()
    shutdown_cond = asyncio.run_coroutine_threadsafe(create_cond(), loop).result()
    service_task = asyncio.run_coroutine_threadsafe(run_service(started_cond, shutdown_cond), loop)
    with started_cond:
        started_cond.wait()
    try:
        yield True
    finally:
        asyncio.run_coroutine_threadsafe(shutdown_service(shutdown_cond), loop).result()
        service_task.result()
        loop.stop()
        for task in asyncio.tasks.all_tasks(loop=loop):
            task.cancel()


class TestSecretStorage():
    def test_default_collection(self):
        bus = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)
        collection.set_label('default')
        assert 'default' == collection.get_label()
        collection.set_label('default')
        assert 'default' == collection.get_label()
        collection.set_label('default1')
        assert 'default1' == collection.get_label()

    def test_search_item(self):
        bus = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)
        collection.create_item('label1', {'attr1': 'val1', 'attr2': 'val2'}, 'secret passphrase')
        collection.create_item('label2', {'attr1': 'val1_tilt', 'attr2': 'val2'}, 'secret passphrase')
        collection.create_item('label3', {'attr1_tilt': 'val1', 'attr2': 'val2'}, 'secret passphrase')
        item_iter = secretstorage.search_items(bus, {'attr1': 'val1'})
        items = [i for i in item_iter]
        labels = [i.get_label() for i in items]
        item_iter = collection.search_items({'attr1': 'val1'})
        coll_labels = [i.get_label() for i in item_iter]
        assert labels == coll_labels
        assert 'label1' in labels
        assert 'label2' not in labels
        assert 'label3' not in labels
        assert b'secret passphrase' == items[0].get_secret()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
