import functools
from PIL import Image

def export_filter(func):
    func.__type__ = "filter"
    func.__return_type__ = None
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def export_tool(func):
    func.__type__ = "tool"
    func.__return_type__ = None
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper