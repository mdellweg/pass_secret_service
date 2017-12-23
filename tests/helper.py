from decorator import decorator
import os
import sys
import shutil
from threading import Thread
import pydbus
from interfaces.service import Service
from common.pass_store import PassStore
from gi.repository import GLib


class LoopThread(Thread):
    def __init__(self, *args, **kwargs):
        super(LoopThread, self).__init__(*args, **kwargs)
        self.mainloop = GLib.MainLoop()

    def run(self):
        self.mainloop.run()

    def exit(self):
        self.mainloop.quit()


class ServiceEnv:
    def __init__(self, clean=True):
        path = os.environ['PASSWORD_STORE_DIR']
        if clean and os.path.exists(os.path.join(path, 'secret_service')):
            shutil.rmtree(os.path.join(path, 'secret_service'))
        self.service = Service(pydbus.SessionBus(), PassStore(path=path))
        self.loop_thread = LoopThread()

    def __enter__(self):
        self.loop_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop_thread.exit()
        self.loop_thread.join()
        self.service._unregister()


@decorator
def with_service(f, *args, **kwargs):
    with ServiceEnv():
        result = f(*args, **kwargs)
    return result
