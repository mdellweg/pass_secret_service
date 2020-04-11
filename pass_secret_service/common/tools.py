import asyncio


def run_in_executor(f):
    async def wraps(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: f(*args, **kwargs))
    return wraps


class SerialMixin:
    _serial_count = 0

    @classmethod
    def _serial(cls):
        cls._serial_count += 1
        return cls._serial_count

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
