# Debug decorator

def debug_me(func):
    """
        Decorator that prints function name before calling the actual function
    """
    def lamb(*args, **kwargs):
        arg_str = ", ".join([str(a) for a in args] + [str(k) + "=" + str(kwargs[k]) for k in kwargs])
        print('#--- {}({}) ---'.format(func.__name__, arg_str))
        result = func(*args, **kwargs)
        print('#--- RES: {} ---'.format(result))
        return result
    return lamb
