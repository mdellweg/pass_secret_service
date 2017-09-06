#!/usr/bin/env python3

import pydbus
from gi.repository import GLib

from common.names import bus_name, base_path

if __name__ == '__main__':
    bus = pydbus.SessionBus()
    service = bus.get(bus_name)
    print(service)
    output, session_path = service.OpenSession('plain', GLib.Variant('s', ''))
    session = bus.get(bus_name, session_path)
    print(session)
    session.Close()
    collection_path, prompt_path = service.CreateCollection({}, '')
    if collection_path == '/':
        print(prompt_path)
        prompt = bus.get(bus_name, prompt_path)
        print(prompt)
        # prompt.Prompt('windowid')
        prompt.Dismiss()
    else:
        print(collection_path)
        collection = bus.get(bus_name, collection_path)
        print(collection)
        print(collection.Locked)
        print(collection.Label)
        collection.Delete()

#    loop = GLib.MainLoop()
#    loop.run()
