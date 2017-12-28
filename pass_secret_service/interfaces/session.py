# Implementation of the org.freedesktop.Secret.Session interface
# TODO unregister when client disconnects from dbus

import os
import pydbus
import hmac
from hashlib import sha256
from cryptography.utils import int_from_bytes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.padding import PKCS7
from gi.repository import GLib

from pass_secret_service.common.debug import debug_me
from pass_secret_service.common.names import base_path
from pass_secret_service.common.tools import SerialMixin
from pass_secret_service.common.consts import dh_prime


class Session(SerialMixin):
    """
      <node>
        <interface name='org.freedesktop.Secret.Session'>
          <method name='Close'/>
        </interface>
      </node>
    """

    @classmethod
    def _create_plain(cls, service):
        return cls(service)

    @classmethod
    def _create_dh(cls, service, input):
        priv_key = int_from_bytes(os.urandom(0x80), 'big')
        pub_key = pow(2, priv_key, dh_prime)
        shared_secret = pow(int_from_bytes(input, 'big'), priv_key, dh_prime)
        salt = b'\x00' * 0x20
        shared_key = hmac.new(salt, shared_secret.to_bytes(0x80, 'big'), sha256).digest()
        aes_key = hmac.new(shared_key, b'\x01', sha256).digest()[:0x10]
        return cls(service, aes_key=aes_key), GLib.Variant('ay', pub_key.to_bytes(0x80, 'big'))

    # secrethelper
    def _encode_secret(self, password):
        aes_iv = []
        password = password.encode('utf8')
        if self.aes_key:
            aes_iv = os.urandom(0x10)
            padder = PKCS7(0x80).padder()
            password = padder.update(password) + padder.finalize()
            encryptor = Cipher(AES(self.aes_key), CBC(aes_iv), default_backend()).encryptor()
            password = encryptor.update(password) + encryptor.finalize()
        return (self.path, aes_iv, password, 'text/plain')

    def _decode_secret(self, secret):
        password = secret[2]
        if self.aes_key:
            aes_iv = bytes(secret[1])
            decryptor = Cipher(AES(self.aes_key), CBC(aes_iv), default_backend()).decryptor()
            password = decryptor.update(password) + decryptor.finalize()
            unpadder = PKCS7(0x80).unpadder()
            password = unpadder.update(password) + unpadder.finalize()
        return bytearray(password).decode('utf8')

    def _unregister(self):
        self.pub_ref.unregister()

    @debug_me
    def __init__(self, service, aes_key=None):
        self.service = service
        self.aes_key = aes_key
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
