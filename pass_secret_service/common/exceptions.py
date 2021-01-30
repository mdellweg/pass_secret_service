from dbus_next import DBusError


class DBusErrorNotSupported(DBusError):
    def __init__(self):
        super().__init__("org.freedesktop.DBus.Error.NotSupported", "This is not supported.")


class DBusErrorIsLocked(DBusError):
    def __init__(self, path):
        super().__init__("org.freedesktop.Secret.Error.IsLocked", "Object is locked: {}.".format(path))


class DBusErrorNoSession(DBusError):
    def __init__(self, path):
        super().__init__("org.freedesktop.Secret.Error.NoSession", "No such session: {}.".format(path))


class DBusErrorNoSuchObject(DBusError):
    def __init__(self, path):
        super().__init__("org.freedesktop.Secret.Error.NoSuchObject", "No such object: {}.".format(path))
