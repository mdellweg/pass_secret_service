import asyncio
import os
import shutil
import sys

from dbus_next.aio import MessageBus

from pass_secret_service.common.names import base_path, bus_name
from pass_secret_service.common.pass_store import PassStore
from pass_secret_service.interfaces.service import Service


async def get_collection(bus, path):
    introspection = await bus.introspect(bus_name, path)
    obj = bus.get_proxy_object(bus_name, path, introspection)
    return obj.get_interface('org.freedesktop.Secret.Collection')


async def get_item(bus, path):
    introspection = await bus.introspect(bus_name, path)
    obj = bus.get_proxy_object(bus_name, path, introspection)
    return obj.get_interface('org.freedesktop.Secret.Item')


async def get_service(bus):
    introspection = await bus.introspect(bus_name, base_path)
    obj = bus.get_proxy_object(bus_name, base_path, introspection)
    return obj.get_interface('org.freedesktop.Secret.Service')


async def get_session(bus, path):
    introspection = await bus.introspect(bus_name, path)
    obj = bus.get_proxy_object(bus_name, path, introspection)
    return obj.get_interface('org.freedesktop.Secret.Session')


class ServiceEnv:
    def __init__(self, clean=True):
        self.path = os.environ['PASSWORD_STORE_DIR']
        if clean and os.path.exists(os.path.join(self.path, 'secret_service')):
            shutil.rmtree(os.path.join(self.path, 'secret_service'))

    async def __aenter__(self):
        self.bus = await MessageBus().connect()
        self.service = await Service._init(self.bus, PassStore(path=self.path))
        await self.bus.request_name(bus_name)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.service._unregister()
        self.bus.disconnect()
