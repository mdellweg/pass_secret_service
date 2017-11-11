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


@decorator
def with_service(f, *args, **kwargs):
    path = os.environ['PASSWORD_STORE_DIR']
    if os.path.exists(os.path.join(path, 'secret_service')):
        shutil.rmtree(os.path.join(path, 'secret_service'))
    service = Service(pydbus.SessionBus(), PassStore(path=path))
    loop_thread = LoopThread()
    loop_thread.start()
    try:
        result = f(*args, **kwargs)
    finally:
        loop_thread.exit()
        loop_thread.join()
        service._unregister()
    return result
