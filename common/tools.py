class SerialMixin:
    _serial_count = 0

    @classmethod
    def _serial(cls):
        cls._serial_count += 1
        return cls._serial_count
