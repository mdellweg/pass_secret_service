# Debug decorator

from decorator import decorator

@decorator
def debug_me(func, *args, **kwargs):
    """
        Decorator that prints function name before calling the actual function
    """
    arg_str = ", ".join([repr(a) for a in args] + [str(k) + "=" + repr(kwargs[k]) for k in kwargs])
    print('#--- {}({}) ---'.format(func.__name__, arg_str))
    try:
        result = func(*args, **kwargs)
        print('#--- RES: {} ---'.format(result))
        return result
    except Exception as err:
        print('#--- FAILED: {} ---'.format(err))
        raise err
