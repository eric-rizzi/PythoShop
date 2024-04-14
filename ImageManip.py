import io

from PythoShopExports import export_filter, export_tool


def create_bmp(width: int, height: int) -> io.BytesIO:
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

    breakpoint()
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
