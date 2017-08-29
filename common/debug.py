# Debug decorator

from decorator import decorator

@decorator
def debug_me(func, *args, **kwargs):
    """
        Decorator that prints function name before calling the actual function
    """
    arg_str = ", ".join([str(a) for a in args] + [str(k) + "=" + str(kwargs[k]) for k in kwargs])
    print('#--- {}({}) ---'.format(func.__name__, arg_str))
    result = func(*args, **kwargs)
    print('#--- RES: {} ---'.format(result))
    return result
