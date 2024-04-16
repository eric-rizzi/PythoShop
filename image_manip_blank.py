import io

from pythoshop_exports import export_filter, export_tool


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
    :param x_y_tuple: An (x, y) tuple that represents the coordinates of a particular pixel
    :returns: None
    """
    image.seek(get_fpp(image) + 3 * ((get_width(image) * x_y_tuple[1] + x_y_tuple[0])))


def get_pixel_rgb(image, x_y_tuple: tuple[int, int]) -> tuple[int, int, int]:
    """
    Helper function to get the RGB value of a particular pixel

    :param image: The bmp bytes
    :param x_y_tuple: An (x, y) tuple that represents the coordinates of a particular pixel
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
    :param x_y_tuple: An (x, y) tuple that represents the coordinates of a particular pixel
    :param r_g_b_tuple: An (r, g, b) tuple that represents color to set pixel to
    :returns: None
    """
    seek_x_y(image, x_y_tuple)
    image.write(int.to_bytes(r_g_b_tuple[2]))
    image.write(int.to_bytes(r_g_b_tuple[1]))
    image.write(int.to_bytes(r_g_b_tuple[0]))
