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

    # secrethelper
    def _encode_secret(self, password):
        return (self.path, [], password.encode('utf8'), 'text/plain')

    def _decode_secret(self, secret):
        return bytearray(secret[2]).decode('utf8')

    def _unregister(self):
        self.pub_ref.unregister()

    @debug_me
    def __init__(self, service):
        self.service = service
        self.bus = self.service.bus
        self.name = 'session{}'.format(self._serial())
        self.path = '{}/session/{}'.format(base_path, self.name)
        # Register with dbus
        self.pub_ref = self.bus.register_object(self.path, self, None)
        # Register with service
        self.service.sessions[self.name] = self

    @debug_me
    def Close(self):
        # Deregister from service
        self.service.sessions.pop(self.name)
        # Deregister from dbus
        self._unregister()
        return None

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
