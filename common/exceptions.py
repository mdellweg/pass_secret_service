# Prepare Exceptions, that get translated into the corresponding DBus errors

class DBusNotSupported(Exception):
    pass
DBusNotSupported.__name__ = "org.freedesktop.DBus.Error.NotSupported"
