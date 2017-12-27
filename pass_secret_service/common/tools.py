class SerialMixin:
    _serial_count = 0

    @classmethod
    def _serial(cls):
        cls._serial_count += 1
        return cls._serial_count

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
