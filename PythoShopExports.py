import functools

def export_filter(func):
    # __type__ = "filter"
    func.__type__ = "filter"
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper

def export_tool(func):
    # __type__ = "tool"
    func.__type__ = "tool"
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper