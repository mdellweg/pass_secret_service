# Implementation of the org.freedesktop.Secret.Session interface
# TODO unregister when client disconnects from dbus

import pydbus
import uuid
from gi.repository import GLib
from common.debug import debug_me

from common.names import base_path

class Session(object):
    """
      <node>
        <interface name='org.freedesktop.Secret.Session'>
          <method name='Close'/>
        </interface>
      </node>
    """
    
    @debug_me
    def __init__(self, bus):
        self.bus = bus
        self.path = base_path + '/session/' + str(uuid.uuid4()).replace('-', '_')
        self.pub_ref = bus.register_object(self.path, self, None)

    @debug_me
    def Close(self):
        self.pub_ref.unregister()
        return None
