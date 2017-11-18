# Prepare Exceptions, that get translated into the corresponding DBus errors


class DBusErrorNotSupported(Exception):
    pass


DBusErrorNotSupported.__name__ = "org.freedesktop.DBus.Error.NotSupported"


class DBusErrorIsLocked(Exception):
    pass


DBusErrorIsLocked.__name__ = "org.freedesktop.Secret.Error.IsLocked"


class DBusErrorNoSession(Exception):
    pass


DBusErrorNoSession.__name__ = "org.freedesktop.Secret.Error.NoSession"


class DBusErrorNoSuchObject(Exception):
    pass


DBusErrorNoSuchObject.__name__ = "org.freedesktop.Secret.Error.NoSuchObject"

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
