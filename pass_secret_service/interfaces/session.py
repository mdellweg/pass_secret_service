# Implementation of the org.freedesktop.Secret.Session interface
# TODO unregister when client disconnects from dbus

import os
import hmac
from hashlib import sha256
from cryptography.utils import int_from_bytes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.padding import PKCS7

from dbus_next.service import (
    method,
    ServiceInterface,
)

from dbus_next import Variant

from pass_secret_service.common.names import base_path
from pass_secret_service.common.tools import run_in_executor, SerialMixin
from pass_secret_service.common.consts import dh_prime


class Session(ServiceInterface, SerialMixin):
    @classmethod
    @run_in_executor
    def _create_dh(cls, input):
        priv_key = int_from_bytes(os.urandom(0x80), 'big')
        pub_key = pow(2, priv_key, dh_prime)
        shared_secret = pow(int_from_bytes(input, 'big'), priv_key, dh_prime)
        salt = b'\x00' * 0x20
        shared_key = hmac.new(salt, shared_secret.to_bytes(0x80, 'big'), sha256).digest()
        aes_key = hmac.new(shared_key, b'\x01', sha256).digest()[:0x10]
        return aes_key, Variant('ay', pub_key.to_bytes(0x80, 'big'))

    # secrethelper
    @run_in_executor
    def _encode_secret(self, password):
        aes_iv = b''
        password = password.encode('utf8')
        if self.aes_key:
            aes_iv = os.urandom(0x10)
            padder = PKCS7(0x80).padder()
            password = padder.update(password) + padder.finalize()
            encryptor = Cipher(AES(self.aes_key), CBC(aes_iv), default_backend()).encryptor()
            password = encryptor.update(password) + encryptor.finalize()
        return [self.path, aes_iv, password, 'text/plain']

    @run_in_executor
    def _decode_secret(self, secret):
        password = secret[2]
        if self.aes_key:
            aes_iv = bytes(secret[1])
            decryptor = Cipher(AES(self.aes_key), CBC(aes_iv), default_backend()).decryptor()
            password = decryptor.update(password) + decryptor.finalize()
            unpadder = PKCS7(0x80).unpadder()
            password = unpadder.update(password) + unpadder.finalize()
        return bytearray(password).decode('utf8')

    async def _unregister(self):
        self.bus.unexport(self.path)

    def __init__(self, service, aes_key=None):
        super().__init__('org.freedesktop.Secret.Session')
        self.service = service
        self.aes_key = aes_key
        self.bus = self.service.bus
        self.id = 'session{}'.format(self._serial())
        self.path = '{}/session/{}'.format(base_path, self.id)
        # Register with dbus
        self.bus.export(self.path, self)
        # Register with service
        self.service.sessions[self.id] = self

    @method()
    async def Close(self) -> '':
        # Deregister from service
        self.service.sessions.pop(self.id)
        # Deregister from dbus
        await self._unregister()
