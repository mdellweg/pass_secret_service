# Implementation of the org.freedesktop.Secret.Session interface
# TODO unregister when client disconnects from dbus

import pydbus
from gi.repository import GLib
from common.debug import debug_me

from common.names import base_path
from common.tools import SerialMixin

class Session(SerialMixin):
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
        self.path = '{}/session/session{}'.format(base_path, self._serial())
        self.pub_ref = bus.register_object(self.path, self, None)

    @debug_me
    def Close(self):
        self.pub_ref.unregister()
        return None
