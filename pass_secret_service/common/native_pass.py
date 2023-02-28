import subprocess
import os

DEFAULT_STORE_DIR = "/tmp/.password-store"
DEFAULT_PASS = "pass"

class NativePasswordStore:
    def __init__(self, use_pass=None, path=None):
        self.pass_cmd = use_pass or DEFAULT_PASS
        self.path = path

    def _pass(self, *args, **kwargs):
        env = os.environ
        if self.path is not None:
            env.update({'PASSWORD_STORE_DIR': self.path})

        proc = subprocess.run([self.pass_cmd, *args],
            check=True,
            text=True,
            capture_output=True,
            env=env,
            **kwargs
        )

        return proc

    def get_decrypted_password(self, passname):
        return self._pass("show", passname).stdout.removesuffix("\n")

    def insert_password(self, passname, password):
        self._pass("insert", "--echo", passname, input=password)
