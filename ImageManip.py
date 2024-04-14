from PIL import Image, ImageDraw

from PythoShopExports import *


def get_fpp(image) -> int:
    """
    Helper function to get the point in a bitmap file where the image "starts"

    :param image: The bmp bytes
    :returns: The index of the byte where the pixels "start"
    """
    image.seek(10)
    return int.from_bytes(image.read(4), byteorder="little")


def get_height(image) -> int:
    """
    Helper function to get the height of a particular bitmap

    :param image: The bmp bytes
    :returns: The height of the bitmap
    """
    image.seek(22)
    return int.from_bytes(image.read(4), byteorder="little")


def get_width(image) -> int:
    """
    Helper function to get the width of a particular bitmap

    :param image: The bmp bytes
    :returns: The width of the bitmap
    """
    image.seek(18)
    return int.from_bytes(image.read(4), byteorder="little")


def seek_x_y(image, x_y_tuple: tuple[int, int]) -> None:
    """
    Helper function to seek to start of the pixel at a given (x, y) coordinate

    :param image: The bmp bytes
    :param x_y_tuble: An (x, y) tuple that represents the coordinates of a particular pixel
    :returns: None
    """
    image.seek(get_fpp(image) + 3 * ((get_width(image) * x_y_tuple[1] + x_y_tuple[0])))


def get_pixel_rgb(image, x_y_tuple: tuple[int, int]) -> tuple[int, int, int]:
    """
    Helper function to get the RGB value of a particular pixel

    :param image: The bmp bytes
    :param x_y_tuble: An (x, y) tuple that represents the coordinates of a particular pixel
    :returns: (r, g, b) tuple
    """
    seek_x_y(image, x_y_tuple)
    b = int.from_bytes(image.read(1))
    g = int.from_bytes(image.read(1))
    r = int.from_bytes(image.read(1))
    return r, g, b


def set_pixel_rgb(image, x_y_tuple: tuple[int, int], r_g_b_tuple: tuple[int, int, int]) -> None:
    """
    Helper function to set the RGB value of a particular pixel

    :param image: The bmp bytes
    :param x_y_tuble: An (x, y) tuple that represents the coordinates of a particular pixel
    :param r_g_b_tuple: An (r, g, b) tuple that represents color to set pixel to
    :returns: None
    """
    seek_x_y(image, x_y_tuple)
    image.write(int.to_bytes(r_g_b_tuple[2]))
    image.write(int.to_bytes(r_g_b_tuple[1]))
    image.write(int.to_bytes(r_g_b_tuple[0]))


@export_tool
def change_pixel(image, clicked_coordinate, **kwargs):
    set_pixel_rgb(image, clicked_coordinate, kwargs["color"])
    print(clicked_coordinate)


@export_filter
def draw_hline(image, color, extra, **kwargs) -> None:

    middle_height = get_height(image) // 2
    width = get_width(image)
    for x in range(width):
        set_pixel_rgb(image, (x, middle_height), color)


@export_filter
def draw_vline(image, color, extra, **kwargs) -> None:

    middle_width = get_width(image) // 2
    height = get_height(image)
    for y in range(height):
        set_pixel_rgb(image, (middle_width, y), color)


@export_filter
def remove_red(image, color, extra, **kwargs) -> None:
    width = get_width(image)
    height = get_height(image)

    for x in range(width):
        for y in range(height):
            r, g, b = get_pixel_rgb(image, (x, y))
            set_pixel_rgb(image, (x, y), (0, g, b))


@export_filter
def remove_green(image, color, extra, **kwargs) -> None:
    width = get_width(image)
    height = get_height(image)

    for x in range(width):
        for y in range(height):
            r, g, b = get_pixel_rgb(image, (x, y))
            set_pixel_rgb(image, (x, y), (r, 0, b))
