# Debug decorator

import sys
import os
from decorator import decorator


def eprint(*args, **kwargs):  # pragma: no cover
    """
        Print to stderr instead of stdout
    """
    print(*args, file=sys.stderr, **kwargs)


def debug_me_fake(func):  # pragma: no cover
    return func


@decorator
def debug_me_real(func, *args, **kwargs):  # pragma: no cover
    """
        Decorator that prints function name before calling the actual function
        also prints its result / error state
    """
    arg_str = ", ".join([repr(a) for a in args] + [str(k) + "=" + repr(kwargs[k]) for k in kwargs])
    eprint('#--- {}({}) ---'.format(func.__name__, arg_str))
    try:
        result = func(*args, **kwargs)
        eprint('#--- RES: {} ---'.format(result))
        return result
    except Exception as err:
        eprint('#--- FAILED: {} ---'.format(err))
        raise err


if os.environ.get('DEBUG_PASS_SECRET_SERVICE'):  # pragma: no branch
    debug_me = debug_me_real  # pragma: no cover
else:
    debug_me = debug_me_fake  # pragma: no cover

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
