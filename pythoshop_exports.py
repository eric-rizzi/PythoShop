"""PythoShop Exports

Defines the decorators used to automatically export functions 
from image_manip.py into the PythoShop GUI application.
"""

import functools


def export_filter(func):
    """Decorator
    describes a function that will be called on an image
    *as a whole* immediately when the user selects it.
    """
    func.__type__ = "filter"
    func.__return_type__ = None

    @functools.wraps(func)
    def wrapper(image, *args, **kwargs):
        return func(image, *args, **kwargs)

    return wrapper


def export_tool(func):
    """Decorator
    describes a function that will get selected and then called
    once the user clicks on a specific position on the image.
    """
    func.__type__ = "tool"
    func.__return_type__ = None

    @functools.wraps(func)
    def wrapper(image, clicked_coordinate, *args, **kwargs):
        return func(image, clicked_coordinate, *args, **kwargs)

    return wrapper
