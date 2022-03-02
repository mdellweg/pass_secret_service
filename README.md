[![Build Status](https://travis-ci.org/mdellweg/pass_secret_service.svg?branch=master)](https://travis-ci.org/mdellweg/pass_secret_service)

# pass_secret_service

expose the libsecret dbus api with pass as backend

# Installing systemd and dbus services
Install [dbus-org.freedesktop.secrets.service](systemd/dbus-org.freedesktop.secrets.service) in `/usr/share/dbus-1/services/` and [org.freedesktop.secrets.service](systemd/org.freedesktop.secrets.service) in `/usr/local/lib/systemd/user/`.  `dbus-org.freedesktop.secrets.service` assumes that the `pass_secret_service` executable is installed in `/usr/local/bin/pass_secret_service`.  If that is not the case on your system, then you will need to modify the `ExecStart` path.

Once these files are in place, you will need to run `systemctl daemon-reload`. Now whenever a program tries to access the libsercret dbus API, dbus should start `pass_secret_service` automatically.

## References

* [secret_service dbus api](https://specifications.freedesktop.org/secret-service/)
* [pass](https://www.passwordstore.org/)
* [pypass](https://github.com/aviau/python-pass)
* [SecretStorage](https://pypi.python.org/pypi/SecretStorage)

>  vim: set ts=2 sw=2 ft=markdown et noro norl cin si ai :
