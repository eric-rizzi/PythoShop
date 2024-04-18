"""PythoShop Exports

Defines the decorators used to automatically export functions 
from image_manip.py into the PythoShop GUI application.
"""

import functools
import io


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


def create_bmp(width: int, height: int) -> io.BytesIO:
    """
    Create a blank bitmap image (all black) that can then be customized by
    setting certain pixels.

    :param width: The width of the new bitmap image
    :param height: The height of the new bitmap image
    :returns: A list of bytes that represent the bitmap image
    """
    row_size = width * 3
    row_padding = 0
    if row_size % 4 != 0:
        row_padding = 4 - row_size % 4
        row_size += row_padding
    bmp = io.BytesIO(b"\x42\x4D" + (138 + row_size * height).to_bytes(4, byteorder="little"))
    bmp.seek(10)
    bmp.write((138).to_bytes(4, byteorder="little"))  # starting pixel
    bmp.write((124).to_bytes(4, byteorder="little"))  # header size (for version 5)
    bmp.write(width.to_bytes(4, byteorder="little"))
    bmp.write(height.to_bytes(4, byteorder="little"))
    bmp.write((1).to_bytes(2, byteorder="little"))  # color planes must be 1
    bmp.write((24).to_bytes(2, byteorder="little"))  # bits per pixel
    bmp.write((0).to_bytes(4, byteorder="little"))  # compression (none)
    bmp.seek(138)
    bmp.write(bytes(([0, 0, 0]) * width + [0] * row_padding) * height)
    return bmp


@functools.lru_cache
def _get_fpp(image) -> int:
    """
    Helper function to get the point in a bitmap file where the image "starts"

    :param image: The bmp bytes
    :returns: The index of the byte where the pixels "start"
    """
    image.seek(10)
    return int.from_bytes(image.read(4), byteorder="little")


@functools.lru_cache
def get_height(image) -> int:
    """
    Helper function to get the height of a particular bitmap

    :param image: The bmp bytes
    :returns: The height of the bitmap
    """
    image.seek(22)
    return int.from_bytes(image.read(4), byteorder="little")


@functools.lru_cache
def get_width(image) -> int:
    """
    Helper function to get the width of a particular bitmap

    :param image: The bmp bytes
    :returns: The width of the bitmap
    """
    image.seek(18)
    return int.from_bytes(image.read(4), byteorder="little")


@functools.lru_cache(maxsize=None)
def _get_padding(image) -> int:
    width = get_width(image)
    row_size = width * 3
    if row_size % 4 != 0:
        return 4 - row_size % 4
    else:
        return 0


def _seek_x_y(image, x_y_tuple: tuple[int, int]) -> None:
    """
    Helper function to seek to start of the pixel at a given (x, y) coordinate

    :param image: The bmp bytes
    :param x_y_tuple: An (x, y) tuple that represents the coordinates of a particular pixel
    :returns: None
    """
    fpp = _get_fpp(image)
    width = get_width(image)
    padding = _get_padding(image)
    image.seek(fpp + ((width * 3 + padding) * x_y_tuple[1]) + (x_y_tuple[0] * 3))


def get_pixel_rgb(image, x_y_tuple: tuple[int, int]) -> tuple[int, int, int]:
    """
    Helper function to get the RGB value of a particular pixel

    :param image: The bmp bytes
    :param x_y_tuple: An (x, y) tuple that represents the coordinates of a particular pixel
    :returns: (r, g, b) tuple
    """
    _seek_x_y(image, x_y_tuple)
    b = int.from_bytes(image.read(1))
    g = int.from_bytes(image.read(1))
    r = int.from_bytes(image.read(1))
    return r, g, b


def set_pixel_rgb(image, x_y_tuple: tuple[int, int], r_g_b_tuple: tuple[int, int, int]) -> None:
    """
    Helper function to set the RGB value of a particular pixel

    :param image: The bmp bytes
    :param x_y_tuple: An (x, y) tuple that represents the coordinates of a particular pixel
    :param r_g_b_tuple: An (r, g, b) tuple that represents color to set pixel to
    :returns: None
    """
    _seek_x_y(image, x_y_tuple)
    image.write(int.to_bytes(r_g_b_tuple[2]))
    image.write(int.to_bytes(r_g_b_tuple[1]))
    image.write(int.to_bytes(r_g_b_tuple[0]))
