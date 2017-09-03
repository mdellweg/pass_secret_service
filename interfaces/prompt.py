# Implementation of the org.freedesktop.Secret.Prompt interface

import pydbus
from pydbus.generic import signal
from gi.repository import GLib

from common.debug import debug_me
from common.names import base_path
from common.tools import SerialMixin

class Prompt(SerialMixin):
    """
      <node>
        <interface name='org.freedesktop.Secret.Prompt'>
          <method name='Prompt'>
            <arg type='s' name='window-id' direction='in'/>
          </method>
          <method name='Dismiss'/>
          <signal name='Completed'>
            <arg type='b' name='dismissed' direction='out'/>
            <arg type='v' name='result' direction='out'/>
          </signal>
        </interface>
      </node>
    """

    @debug_me
    def __init__(self, bus):
        self.bus = bus
        self.path = '{}/prompt/prompt{}'.format(base_path, self._serial())
        self.pub_ref = bus.register_object(self.path, self, None)

    @debug_me
    def Prompt(self, window_id):
        pass

    @debug_me
    def Dismiss(self):
        self.pub_ref.unregister()
        return None

    Completed = signal()
