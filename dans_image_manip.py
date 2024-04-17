import io
import math
import random

from pythoshop_exports import *


# Helper functions
def create_bmp(width, height):
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


def distance(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def color_distance(color1, color2):
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])


def go_to(image, coordinate):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    image.seek(first_pixel + row_size * coordinate[1] + 3 * coordinate[0])


def get_info(image):
    """
    Get information from the header of a BMP file
    :param image: and already-open BMP file with read permission
    :return: tuple containing (in this order):
        the first pixel location
        width
        height
        bits per pixel
        row size
        row padding
    """
    image.seek(10)
    first_pixel_index = int.from_bytes(image.read(4), "little")
    image.seek(18)
    width = int.from_bytes(image.read(4), "little")
    height = int.from_bytes(image.read(4), "little")
    image.seek(28)
    bpp = int.from_bytes(image.read(2), "little")
    if bpp != 24:
        raise ValueError("Unsupported bits per pixel")
    row_size = width * 3
    # Rows need to be padded to a multiple of 4 bytes
    row_padding = 0
    if row_size % 4 != 0:
        row_padding = 4 - row_size % 4
        row_size += row_padding
    return first_pixel_index, width, height, bpp, row_size, row_padding


# Lesson: change a pixel


@export_tool
def change_pixel(image, clicked_coordinate, **kwargs):
    """Implementation with the extension"""
    fpp, width, height, bpp, row_size, padding = get_info(image)
    x, y = clicked_coordinate
    try:
        radius = int(kwargs["extra"])
    except:
        radius = 0
    length = radius * 2 + 1
    if x - radius >= 0:
        start_x = x - radius
    else:
        start_x = 0
        length += x - radius
    if x + radius + 1 > width:
        length -= x + radius + 1 - width
    for row in range(max(y - radius, 0), y + radius + 1):
        image.seek(fpp + (width * 3 + padding) * row + start_x * 3)
        image.write(bytes([kwargs["color"][2], kwargs["color"][1], kwargs["color"][0]] * (length)))


@export_filter
def mark_middle(image, **kwargs):
    fpp, width, height, bpp, row_size, padding = get_info(image)
    kwargs.pop("clicked_coordinate")
    change_pixel(image, (round(width / 2), round(height / 2)), **kwargs)


# Lesson: Draw some lines


@export_tool
def draw_hline(image, clicked_coordinate, **kwargs):
    fpp, width, height, bpp, row_size, padding = get_info(image)
    x, y = clicked_coordinate
    color = list(reversed(kwargs["color"]))  # get it in bitmap (BGR) order
    try:
        thickness = int(kwargs["extra"])
    except:
        thickness = 1
    start_row = y - round(thickness / 2)
    row_of_pixels = color * width + [0] * padding
    image.seek(fpp + row_size * start_row)
    image.write(bytes(row_of_pixels))


@export_tool
def draw_vline(image, clicked_coordinate, **kwargs):
    fpp, width, height, bpp, row_size, padding = get_info(image)
    x, y = clicked_coordinate
    color = bytes(list(reversed(kwargs["color"])))
    try:
        thickness = int(kwargs["extra"])
    except:
        thickness = 1
    start_x = x - round(thickness / 2)
    image.seek(fpp + start_x * 3)
    for row in range(height):
        image.write(color * thickness)
        image.seek(row_size - thickness * 3, 1)


@export_filter
def draw_centered_hline(image, **kwargs):
    fpp, width, height, bpp, row_size, padding = get_info(image)
    draw_hline(image, (0, round(height / 2)), **kwargs)


@export_filter
def draw_centered_vline(image, **kwargs):
    fpp, width, height, bpp, row_size, padding = get_info(image)
    draw_vline(image, (round(width / 2), 0), **kwargs)


@export_filter
def draw_bisecting_diagonals(image, **kwargs):
    # extra could be a width
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    bmp_color = (kwargs["color"][2], kwargs["color"][1], kwargs["color"][0])
    image.seek(first_pixel)
    for y in range(height):
        image.seek(first_pixel + row_size * y)
        before = 0
        length = 0
        for x in range(width):
            if x / width < y / height:
                image.seek(3, 1)
                before += 1
            else:
                image.write(bytes(bmp_color))
                x += 1
                length += 1
                while x / width < (y + 1) / height:
                    image.write(bytes(bmp_color))
                    x += 1
                    length += 1
                break
        image.seek(3 * (width - 2 * (before + length)), 1)
        for pixel in range(length):
            image.write(bytes(bmp_color))


# Lesson: Changing parts of a pixel

# @export_filter
# def make_red(image, **kwargs):
#     """The simple version that doesn't take padding into account"""
#     # extra could be the intensity of the red
#     fpp, width, height, bpp, row_size, padding = get_info(image)
#     image.seek(fpp)
#     for row in range(height):  # go through every row in the image
#         for pixel in range(width):  # go through every pixel in the current row
#             image.write(bytes([0, 0, 255]))


@export_filter
def make_red(image, **kwargs):
    # extra could be the intensity of the red
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)  # makes it go to the beginning of the row taking padding into account
        for pixel in range(width):  # go through every pixel in the current row
            image.write(bytes([0, 0, 255]))
        # Alternatively could skip past the padding here
        # image.seek(padding, 1)


@export_filter
def make_static(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    try:
        distance = int(kwargs["extra"])
    except (KeyError, ValueError):
        distance = 255
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.write(
                bytes(
                    [
                        random.randint(max(0, kwargs["color"][2] - distance), min(255, kwargs["color"][2] + distance)),
                        random.randint(max(0, kwargs["color"][1] - distance), min(255, kwargs["color"][1] + distance)),
                        random.randint(max(0, kwargs["color"][0] - distance), min(255, kwargs["color"][0] + distance)),
                    ]
                )
            )


@export_filter
def remove_red(image, **kwargs):
    # extra could be how much to remove
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.seek(2, 1)
            image.write(bytes([0]))


@export_filter
def remove_green(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.seek(1, 1)
            image.write(bytes([0]))
            image.seek(1, 1)


@export_filter
def remove_blue(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.write(bytes([0]))
            image.seek(2, 1)


@export_filter
def max_red(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.seek(2, 1)
            image.write(bytes([255]))


@export_filter
def max_green(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.seek(1, 1)
            image.write(bytes([255]))
            image.seek(1, 1)


@export_filter
def max_blue(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            image.write(bytes([255]))
            image.seek(2, 1)


@export_filter
def only_blue(image, **kwargs):
    remove_red(image, **kwargs)
    remove_green(image, **kwargs)


@export_filter
def only_green(image, **kwargs):
    remove_red(image, **kwargs)
    remove_blue(image, **kwargs)


@export_filter
def only_red(image, **kwargs):
    remove_blue(image, **kwargs)
    remove_green(image, **kwargs)


# Lesson: Change pixel based on its current value


@export_filter
def lighten(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([min(255, round(b * 1.5)), min(255, round(g * 1.5)), min(255, round(r * 1.5))]))


@export_filter
def darken(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([round(b / 2), round(g / 2), round(r / 2)]))


@export_filter
def make_gray(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            grey = round(brightness / 3)
            image.seek(-3, 1)
            image.write(bytes([grey, grey, grey]))


@export_filter
def negate(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([255 - b, 255 - g, 255 - r]))


@export_filter
def negate_red(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([b, g, 255 - r]))


@export_filter
def negate_green(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([b, 255 - g, r]))


@export_filter
def negate_blue(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([255 - b, g, r]))


# ? just have 1 swap where extra is 3 characters bgr in any order


@export_filter
def swap_gbr(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([g, b, r]))


@export_filter
def swap_rgb(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([r, g, b]))


@export_filter
def swap_brg(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([b, r, g]))


@export_filter
def swap_rbg(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([r, b, g]))


@export_filter
def swap_grb(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(bytes([g, r, b]))


@export_filter
def grayify(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            avg_brightness = (b + g + r) / 3
            b = round((b + avg_brightness) / 2)
            g = round((g + avg_brightness) / 2)
            r = round((r + avg_brightness) / 2)
            image.seek(-3, 1)
            image.write(bytes([b, g, r]))


@export_filter
def redify(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < 382.5:
                r = round(brightness / 382.5 * 255)
                image.write(bytes([0, 0, r]))
            else:
                bg = round((brightness - 382.5) / 382.5 * 255)
                image.write(bytes([bg, bg, 255]))


@export_filter
def greenify(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < 382.5:
                g = round(brightness / 382.5 * 255)
                image.write(bytes([0, g, 0]))
            else:
                br = round((brightness - 382.5) / 382.5 * 255)
                image.write(bytes([br, 255, br]))


@export_filter
def blueify(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < 382.5:
                b = round(brightness / 382.5 * 255)
                image.write(bytes([b, 0, 0]))
            else:
                gr = round((brightness - 382.5) / 382.5 * 255)
                image.write(bytes([255, gr, gr]))


@export_filter
def magentify(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < 382.5:
                br = round(brightness / 382.5 * 255)
                image.write(bytes([br, 0, br]))
            else:
                g = round((brightness - 382.5) / 382.5 * 255)
                image.write(bytes([255, g, 255]))


# Lesson: Conditional modifications


@export_filter
def intensify(image, **kwargs):
    try:
        intensification = float(kwargs["extra"])
    except (ValueError, KeyError):
        intensification = 1.0
    if intensification > 1 or intensification < 0:
        raise ValueError("The intensification (extra) must be between 0 and 1")
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
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


@export_filter
def make_two_tone(image, **kwargs):
    light = kwargs["color"]
    try:
        dark = [int(x) for x in kwargs["extra"].split(",")]
        if len(dark) != 3:
            dark = (0, 0, 0)
    except (ValueError, KeyError):
        dark = (0, 0, 0)
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < 382.5:
                image.write(bytes([dark[2], dark[1], dark[0]]))
            else:
                image.write(bytes([light[2], light[1], light[0]]))


@export_filter
def make_four_tone(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    r, g, b = kwargs["color"]
    r_delta = r / 3
    g_delta = g / 3
    b_delta = b / 3
    darker = (0, 0, 0)
    dark = (int(r_delta), int(g_delta), int(b_delta))
    medium = (int(r_delta * 2), int(g_delta * 2), int(b_delta * 2))
    light = kwargs["color"]
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < 191.5:
                image.write(bytes([darker[2], darker[1], darker[0]]))
            elif brightness < 382.5:
                image.write(bytes([dark[2], dark[1], dark[0]]))
            elif brightness < 573.75:
                image.write(bytes([medium[2], medium[1], medium[0]]))
            else:
                image.write(bytes([light[2], light[1], light[0]]))


@export_filter
def make_n_tone(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    try:
        n = int(kwargs["extra"])
    except (ValueError, KeyError):
        raise ValueError("Extra has to be an integer intdicating the number of levels")
    r, g, b = kwargs["color"]
    r_delta = r / (n - 1)
    g_delta = g / (n - 1)
    b_delta = b / (n - 1)
    bmp_tones = []
    for level in range(n):
        bmp_tones.append((int(b_delta * level), int(g_delta * level), int(r_delta * level)))
    brightness_interval = 765 / n
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            tone = bmp_tones[min(int(brightness / brightness_interval), n - 1)]
            image.seek(-3, 1)
            image.write(bytes(tone))


@export_filter
def saturate(image, **kwargs):
    def calc_mid(max, mid, min):
        """
        Only helper functions (like this) should be defined inside of other functions
        :param max: dominant color value
        :param mid: middle color value
        :param min: minimal color value
        :return: middle color value that is proporitionally the same distance between 0 and 255
        """
        return round((mid - min) / (max - min) * 255)

    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            if b > g and b > r:  # blue is max
                if g < r:  # green is min
                    r = calc_mid(b, r, g)
                    b = 255
                    g = 0
                else:  # red is min
                    g = calc_mid(b, g, r)
                    b = 255
                    r = 0
            elif g > b and g > r:  # green is max
                if b < r:  # blue is min
                    r = calc_mid(g, r, b)
                    g = 255
                    b = 0
                else:  # red is min
                    b = calc_mid(g, b, r)
                    g = 255
                    r = 0
            elif r > b and r > g:  # red is max
                if b < g:  # blue is min
                    g = calc_mid(r, g, b)
                    r = 255
                    b = 0
                else:  # green is min
                    b = calc_mid(r, b, g)
                    r = 255
                    g = 0
            else:  # no one color dominates
                if g > r and b > r:  # green and blue are max
                    r = 0
                    # r = calc_mid(g, r, 0)
                    g = 255
                    b = 255
                elif r > g and b > g:  # red and blue are max
                    # g = calc_mid(r, g, 0)
                    g = 0
                    r = 255
                    b = 255
                elif r > b and g > b:  # red and green are max
                    # b = calc_mid(r, b, 0)
                    b = 0
                    r = 255
                    g = 255
                else:  # all colors are the same: make it white
                    r = 255
                    b = 255
                    g = 255
            image.seek(-3, 1)
            image.write(bytes([b, g, r]))


# Lesson: Multiple pixel formulas


@export_filter
def make_better_two_tone(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    light = kwargs["color"]
    try:
        dark = [int(x) for x in kwargs["extra"].split(",")]
        if len(dark) != 3:
            dark = (0, 0, 0)
    except (ValueError, KeyError):
        dark = (0, 0, 0)
    total_brightness = 0
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            total_brightness += b + g + r
    avg_brightness = total_brightness / (width * height)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            brightness = b + g + r
            image.seek(-3, 1)
            if brightness < avg_brightness:
                image.write(bytes((dark[2], dark[1], dark[0])))
            else:
                image.write(bytes((light[2], light[1], light[0])))


@export_filter
def blend_other(image, other_image, **kwargs):
    try:
        percentage1 = float(kwargs["extra"])
    except (ValueError, KeyError):
        percentage1 = 0.5

    if percentage1 < 0 or percentage1 > 1:
        raise ValueError("The extra parameter must be a percentage (between 0 and 1)")
    percentage2 = 1 - percentage1
    image1_first_pixel, image1_width, image1_height, image1_bpp, image1_row_size, image1_row_padding = get_info(image)
    image2_first_pixel, image2_width, image2_height, image2_bpp, image2_row_size, image2_row_padding = get_info(other_image)
    min_height = min(image1_height, image2_height)
    min_width = min(image1_width, image2_width)
    result = create_bmp(min_width, min_height)
    result_first_pixel, result_width, result_height, result_bpp, result_row_size, result_row_padding = get_info(result)
    for row in range(min_height):  # go through overlapping rows in the images
        image.seek(image1_first_pixel + row * image1_row_size)
        other_image.seek(image2_first_pixel + row * image2_row_size)
        result.seek(result_first_pixel + row * result_row_size)
        for pixel in range(min_width):  # go through overlapping pixels in the current row
            b1, g1, r1 = image.read(3)
            b2, g2, r2 = other_image.read(3)
            result.write(
                bytes([round(b1 * percentage1 + b2 * percentage2), round(g1 * percentage1 + g2 * percentage2), round(r1 * percentage1 + r2 * percentage2)])
            )
    result.seek(0)
    return result


@export_filter
def chroma_overlay(image, other_image, **kwargs):
    background_image = image
    foreground_image = other_image
    bg_first_pixel, bg_width, bg_height, bg_bpp, bg_row_size, bg_row_padding = get_info(background_image)
    fg_first_pixel, fg_width, fg_height, fg_bpp, fg_row_size, fg_row_padding = get_info(foreground_image)
    target_chroma = kwargs["color"]
    try:
        tolerance = int(kwargs["extra"])
    except (ValueError, KeyError):
        tolerance = 100

    result = create_bmp(bg_width, bg_height)
    res_first_pixel, res_width, res_height, res_bpp, res_row_size, res_row_padding = get_info(result)
    for row in range(res_height):  # go through overlapping rows in the images
        for pixel in range(res_width):  # go through overlapping pixels in the current row
            result.seek(res_first_pixel + row * res_row_size + pixel * 3)
            background_image.seek(bg_first_pixel + row * bg_row_size + pixel * 3)
            b1, g1, r1 = background_image.read(3)
            if row >= 0 and row < fg_height and pixel >= 0 and pixel < fg_width:
                foreground_image.seek(fg_first_pixel + row * fg_row_size + pixel * 3)
                b2, g2, r2 = foreground_image.read(3)
                if color_distance((b2, g2, r2), (target_chroma[2], target_chroma[1], target_chroma[0])) < tolerance:
                    result.write(bytes([b1, g1, r1]))
                else:
                    result.write(bytes([b2, g2, r2]))
            else:
                result.write(bytes([b1, g1, r1]))
    result.seek(0)
    return result


# Lesson: Pixel positions


@export_filter
def fade_in_vertical(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        percent = row / (height - 1)
        converse = 1 - percent
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(
                bytes(
                    [
                        round(b * percent + kwargs["color"][2] * converse),
                        round(g * percent + kwargs["color"][1] * converse),
                        round(r * percent + kwargs["color"][0] * converse),
                    ]
                )
            )


@export_filter
def fade_out_vertical(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        percent = 1 - row / (height - 1)
        converse = 1 - percent
        for pixel in range(width):  # go through every pixel in the current row
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(
                bytes(
                    [
                        round(b * percent + kwargs["color"][2] * converse),
                        round(g * percent + kwargs["color"][1] * converse),
                        round(r * percent + kwargs["color"][0] * converse),
                    ]
                )
            )


@export_filter
def fade_in_horizontal(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            percent = pixel / (width - 1)
            converse = 1 - percent
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(
                bytes(
                    [
                        round(b * percent + kwargs["color"][2] * converse),
                        round(g * percent + kwargs["color"][1] * converse),
                        round(r * percent + kwargs["color"][0] * converse),
                    ]
                )
            )


@export_filter
def fade_out_horizontal(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        image.seek(first_pixel + row * row_size)
        for pixel in range(width):  # go through every pixel in the current row
            percent = 1 - pixel / (width - 1)
            converse = 1 - percent
            b, g, r = image.read(3)
            image.seek(-3, 1)
            image.write(
                bytes(
                    [
                        round(b * percent + kwargs["color"][2] * converse),
                        round(g * percent + kwargs["color"][1] * converse),
                        round(r * percent + kwargs["color"][0] * converse),
                    ]
                )
            )


@export_filter
def make_line_drawing(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    try:
        tolerance = int(kwargs["extra"])
    except:
        tolerance = 10
    new_image = create_bmp(width - 1, height)
    new_first_pixel, new_width, new_height, new_bpp, new_row_size, new_row_padding = get_info(new_image)
    for row in range(new_height):
        for pixel in range(new_width):
            image.seek(first_pixel + row * row_size + pixel * 3)
            b1, g1, r1, b2, g2, r2 = image.read(6)
            new_image.seek(new_first_pixel + row * new_row_size + pixel * 3)
            if abs((b1 + g1 + r1) - (b2 + g2 + r2)) > tolerance:
                new_image.write(bytes([kwargs["color"][2], kwargs["color"][1], kwargs["color"][0]]))
            else:
                new_image.write(bytes([255, 255, 255]))
    return new_image


@export_filter
def mirror_bottom_vertical(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(int(height / 2)):  # go through every row in the image
        for pixel in range(width):  # go through every pixel in the current row
            image.seek(first_pixel + row * row_size + pixel * 3)
            b, g, r = image.read(3)
            image.seek(first_pixel + (height - 1 - row) * row_size + pixel * 3)
            image.write(bytes([b, g, r]))


@export_filter
def mirror_top_vertical(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height - 1, int(height / 2), -1):  # go through every row in the image
        for pixel in range(width):  # go through every pixel in the current row
            image.seek(first_pixel + row * row_size + pixel * 3)
            b, g, r = image.read(3)
            image.seek(first_pixel + (height - 1 - row) * row_size + pixel * 3)
            image.write(bytes([b, g, r]))


@export_filter
def mirror_left_horizontal(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        for pixel in range(int(width / 2)):  # go through every pixel in the current row
            image.seek(first_pixel + row * row_size + pixel * 3)
            b, g, r = image.read(3)
            image.seek(first_pixel + row * row_size + (width - 1 - pixel) * 3)
            image.write(bytes([b, g, r]))


@export_filter
def mirror_right_horizontal(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    for row in range(height):  # go through every row in the image
        for pixel in range(width - 1, int(width / 2), -1):  # go through every pixel in the current row
            image.seek(first_pixel + row * row_size + pixel * 3)
            b, g, r = image.read(3)
            image.seek(first_pixel + row * row_size + (width - 1 - pixel) * 3)
            image.write(bytes([b, g, r]))


# TODO: doesn't look it in the GUI
# TODO: doesn't handle edge case where the original image is only 1 pixel wide / tall
# TODO: could use extra as a shrink factor
@export_filter
def shrink(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    small_image = create_bmp(round(width / 2), round(height / 2))
    sm_first_pixel, sm_width, sm_height, sm_bpp, sm_row_size, sm_row_padding = get_info(small_image)
    for row in range(0, height, 2):  # go through every other row in the image
        for pixel in range(0, width, 2):  # go through every other pixel in the current row
            image.seek(first_pixel + row * row_size + pixel * 3)
            b, g, r = image.read(3)
            small_image.seek(sm_first_pixel + int(row / 2) * sm_row_size + int(pixel / 2) * 3)
            small_image.write(bytes([b, g, r]))
    return small_image


@export_filter
def better_shrink(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    small_image = create_bmp(int(width / 2), int(height / 2))
    sm_first_pixel, sm_width, sm_height, sm_bpp, sm_row_size, sm_row_padding = get_info(small_image)
    for row in range(sm_height):
        for pixel in range(sm_width):
            image.seek(first_pixel + row * 2 * row_size + pixel * 2 * 3)
            b1, g1, r1, b2, g2, r2 = image.read(6)
            image.seek(first_pixel + (row * 2 + 1) * row_size + pixel * 2 * 3)
            b3, g3, r3, b4, g4, r4 = image.read(6)
            small_image.seek(sm_first_pixel + row * sm_row_size + pixel * 3)
            small_image.write(bytes([round((b1 + b2 + b3 + b4) / 4), round((g1 + g2 + g3 + g4) / 4), round((r1 + r2 + r3 + r4) / 4)]))
    return small_image


@export_filter
def enlarge(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    large_image = create_bmp(width * 2, height * 2)
    lg_first_pixel, lg_width, lg_height, lg_bpp, lg_row_size, lg_row_padding = get_info(large_image)
    for row in range(height):
        for pixel in range(width):
            image.seek(first_pixel + row * row_size + pixel * 3)
            b, g, r = image.read(3)
            large_image.seek(lg_first_pixel + row * 2 * lg_row_size + pixel * 2 * 3)
            large_image.write(bytes([b, g, r] * 2))
            large_image.seek(lg_first_pixel + (row * 2 + 1) * lg_row_size + pixel * 2 * 3)
            large_image.write(bytes([b, g, r] * 2))
    return large_image


@export_filter
def better_enlarge(image, **kwargs):
    enlarged = enlarge(image)
    first_pixel, width, height, bpp, row_size, row_padding = get_info(enlarged)
    smoothed = create_bmp(width, height)
    # All pixels that have 4 around them
    for row in range(1, height - 1):
        for pixel in range(1, width - 1):
            enlarged.seek(first_pixel + (row - 1) * row_size + pixel * 3)
            bd, gd, rd = enlarged.read(3)
            enlarged.seek(first_pixel + (row + 1) * row_size + pixel * 3)
            bu, gu, ru = enlarged.read(3)
            enlarged.seek(first_pixel + row * row_size + (pixel - 1) * 3)
            bl, gl, rl, b, g, r, br, gr, rr = enlarged.read(9)
            b_avg = round((bu + bd + bl + b + br) / 5)
            g_avg = round((gu + gd + gl + g + gr) / 5)
            r_avg = round((ru + rd + rl + r + rr) / 5)
            smoothed.seek(first_pixel + row * row_size + pixel * 3)
            smoothed.write(bytes([b_avg, g_avg, r_avg]))
    # All pixels on the top and bottom edges
    for pixel in range(1, width - 1):
        row = 0
        enlarged.seek(first_pixel + (row + 1) * row_size + pixel * 3)
        bu, gu, ru = enlarged.read(3)
        enlarged.seek(first_pixel + row * row_size + (pixel - 1) * 3)
        bl, gl, rl, b, g, r, br, gr, rr = enlarged.read(9)
        b_avg = round((bu + bl + b + br) / 4)
        g_avg = round((gu + gl + g + gr) / 4)
        r_avg = round((ru + rl + r + rr) / 4)
        smoothed.seek(first_pixel + row * row_size + pixel * 3)
        smoothed.write(bytes([b_avg, g_avg, r_avg]))

        row = height - 1
        enlarged.seek(first_pixel + (row - 1) * row_size + pixel * 3)
        bd, gd, rd = enlarged.read(3)
        enlarged.seek(first_pixel + row * row_size + (pixel - 1) * 3)
        bl, gl, rl, b, g, r, br, gr, rr = enlarged.read(9)
        b_avg = round((bd + bl + b + br) / 4)
        g_avg = round((gd + gl + g + gr) / 4)
        r_avg = round((rd + rl + r + rr) / 4)
        smoothed.seek(first_pixel + row * row_size + pixel * 3)
        smoothed.write(bytes([b_avg, g_avg, r_avg]))
    # All pixels on the left and right edges
    for row in range(1, height - 1):
        pixel = 0
        enlarged.seek(first_pixel + (row - 1) * row_size + pixel * 3)
        bd, gd, rd = enlarged.read(3)
        enlarged.seek(first_pixel + (row + 1) * row_size + pixel * 3)
        bu, gu, ru = enlarged.read(3)
        enlarged.seek(first_pixel + row * row_size + pixel * 3)
        b, g, r, br, gr, rr = enlarged.read(6)
        b_avg = round((bu + bd + b + br) / 4)
        g_avg = round((gu + gd + g + gr) / 4)
        r_avg = round((ru + rd + r + rr) / 4)
        smoothed.seek(first_pixel + row * row_size + pixel * 3)
        smoothed.write(bytes([b_avg, g_avg, r_avg]))

        pixel = width - 1
        enlarged.seek(first_pixel + (row - 1) * row_size + pixel * 3)
        bd, gd, rd = enlarged.read(3)
        enlarged.seek(first_pixel + (row + 1) * row_size + pixel * 3)
        bu, gu, ru = enlarged.read(3)
        enlarged.seek(first_pixel + row * row_size + (pixel - 1) * 3)
        bl, gl, rl, b, g, r = enlarged.read(6)
        b_avg = round((bu + bd + bl + b) / 4)
        g_avg = round((gu + gd + gl + g) / 4)
        r_avg = round((ru + rd + rl + r) / 4)
        smoothed.seek(first_pixel + row * row_size + pixel * 3)
        smoothed.write(bytes([b_avg, g_avg, r_avg]))
    # Corner pixels
    row = 0
    pixel = 0
    enlarged.seek(first_pixel + (row + 1) * row_size + pixel * 3)
    bu, gu, ru = enlarged.read(3)
    enlarged.seek(first_pixel + row * row_size + pixel * 3)
    b, g, r, br, gr, rr = enlarged.read(6)
    b_avg = round((bu + b + br) / 3)
    g_avg = round((gu + g + gr) / 3)
    r_avg = round((ru + r + rr) / 3)
    smoothed.seek(first_pixel + row * row_size + pixel * 3)
    smoothed.write(bytes([b_avg, g_avg, r_avg]))

    row = height - 1
    pixel = 0
    enlarged.seek(first_pixel + (row - 1) * row_size + pixel * 3)
    bd, gd, rd = enlarged.read(3)
    enlarged.seek(first_pixel + row * row_size + pixel * 3)
    b, g, r, br, gr, rr = enlarged.read(6)
    b_avg = round((bd + b + br) / 3)
    g_avg = round((gd + g + gr) / 3)
    r_avg = round((rd + r + rr) / 3)
    smoothed.seek(first_pixel + row * row_size + pixel * 3)
    smoothed.write(bytes([b_avg, g_avg, r_avg]))

    row = height - 1
    pixel = width - 1
    enlarged.seek(first_pixel + (row - 1) * row_size + pixel * 3)
    bd, gd, rd = enlarged.read(3)
    enlarged.seek(first_pixel + row * row_size + (pixel - 1) * 3)
    bl, gl, rl, b, g, r = enlarged.read(6)
    b_avg = round((bd + bl + b) / 3)
    g_avg = round((gd + gl + g) / 3)
    r_avg = round((rd + rl + r) / 3)
    smoothed.seek(first_pixel + row * row_size + pixel * 3)
    smoothed.write(bytes([b_avg, g_avg, r_avg]))

    row = 0
    pixel = width - 1
    enlarged.seek(first_pixel + (row + 1) * row_size + pixel * 3)
    bu, gu, ru = enlarged.read(3)
    enlarged.seek(first_pixel + row * row_size + (pixel - 1) * 3)
    bl, gl, rl, b, g, r = enlarged.read(6)
    b_avg = round((bu + bl + b) / 3)
    g_avg = round((gu + gl + g) / 3)
    r_avg = round((ru + rl + r) / 3)
    smoothed.seek(first_pixel + row * row_size + pixel * 3)
    smoothed.write(bytes([b_avg, g_avg, r_avg]))

    return smoothed


@export_filter
def resize(image, **kwargs):
    first_pixel, width, height, bpp, row_size, row_padding = get_info(image)
    try:
        multiplier = float(kwargs["extra"])
    except:
        raise ValueError("Extra parameter (the multiplier) must be specified")
    if multiplier <= 0:
        raise ValueError("Extra parameter (multiplier) must be greater than zero")
    new_image = create_bmp(int(width * multiplier), int(height * multiplier))
    new_first_pixel, new_width, new_height, new_bpp, new_row_size, new_row_padding = get_info(new_image)
    if multiplier < 0:
        raise ValueError("Resize multiplier can't be negative")
    for row in range(new_height):  # go through every other row in the image
        for pixel in range(new_width):  # go through every other pixel in the current row
            image.seek(first_pixel + int(row * 1 / multiplier) * row_size + int(pixel * 1 / multiplier) * 3)
            b, g, r = image.read(3)
            new_image.seek(new_first_pixel + row * new_row_size + pixel * 3)
            new_image.write(bytes([b, g, r]))
    return new_image
