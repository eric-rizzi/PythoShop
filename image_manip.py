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


@export_tool
def change_pixel(image, clicked_coordinate, **kwargs):
    set_pixel_rgb(image, clicked_coordinate, kwargs["color"])


@export_filter
def draw_hline(image, color, extra="0", **kwargs) -> None:

    middle_height = get_height(image) // 2
    width = get_width(image)
    for x in range(width):
        set_pixel_rgb(image, (x, middle_height), color)


@export_filter
def draw_vline(image, color, extra="0", **kwargs) -> None:

    middle_width = get_width(image) // 2
    height = get_height(image)
    for y in range(height):
        set_pixel_rgb(image, (middle_width, y), color)


@export_filter
def remove_red(image, color, extra="0", **kwargs) -> None:
    width = get_width(image)
    height = get_height(image)

    for x in range(width):
        for y in range(height):
            r, g, b = get_pixel_rgb(image, (x, y))
            set_pixel_rgb(image, (x, y), (0, g, b))


@export_filter
def remove_green(image, color, extra="0", **kwargs) -> None:
    width = get_width(image)
    height = get_height(image)

    for x in range(width):
        for y in range(height):
            r, g, b = get_pixel_rgb(image, (x, y))
            set_pixel_rgb(image, (x, y), (r, 0, b))


@export_filter
def blend_other(image: io.BytesIO, other_image: io.BytesIO, color: tuple[int, int, int], extra="0.5", **kwargs) -> io.BytesIO:
    try:
        percentage1 = float(extra)
    except ValueError:
        percentage1 = 0.5
    if percentage1 < 0 or percentage1 > 1:
        raise ValueError("The extra parameter must be a percentage (between 0 and 1)")

    percentage2 = 1 - percentage1

    width_1 = get_width(image)
    width_2 = get_width(other_image)
    min_width = min(width_1, width_2)

    height_1 = get_height(image)
    height_2 = get_height(other_image)
    min_height = min(height_1, height_2)

    result = create_bmp(min_width, min_height)

    for x in range(min_width):  # go through overlapping rows in the images
        for y in range(min_height):
            r1, g1, b1 = get_pixel_rgb(image, (x, y))
            r2, g2, b2 = get_pixel_rgb(other_image, (x, y))
            set_pixel_rgb(
                result,
                (x, y),
                (round(r1 * percentage1 + r2 * percentage2), round(g1 * percentage1 + g2 * percentage2), round(b1 * percentage1 + b2 * percentage2)),
            )

    result.seek(0)
    return result


@export_filter
def draw_centered_hline(image, color, extra="0", **kwargs) -> None:
    draw_hline(image, color, extra, kwargs=kwargs)


@export_filter
def draw_centered_vline(image, color, extra="0", **kwargs) -> None:
    draw_vline(image, color, extra, kwargs=kwargs)


@export_filter
def intensify(image, color, extra="1.0", **kwargs):
    try:
        intensification = float(extra)
    except ValueError:
        intensification = 1
    if intensification > 1 or intensification < 0:
        raise ValueError("The intensification (extra) must be between 0 and 1")

    first_pixel = get_fpp(image)
    width = get_width(image)
    height = get_height(image)

    row_size = width * 3
    # Rows need to be padded to a multiple of 4 bytes
    row_padding = 0
    if row_size % 4 != 0:
        row_padding = 4 - row_size % 4
        row_size += row_padding

    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            if b > 127.5:
                b = round(b + (255 - b) * intensification)
            else:
                b = round(b - b * intensification)
            if g > 127.5:
                g = round(g + (255 - g) * intensification)
            else:
                g = round(g - g * intensification)
            if r > 127.5:
                r = round(r + (255 - r) * intensification)
            else:
                r = round(r - r * intensification)
            image.seek(-3, 1)
            image.write(bytes([b, g, r]))
