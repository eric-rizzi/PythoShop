from pythoshop_exports import create_bmp, export_filter, export_tool, get_height, get_pixel_rgb, get_width, set_pixel_rgb


@export_tool
def change_pixel(image, clicked_coordinate, color, **kwargs):
    x, y = clicked_coordinate
    r, g, b = color
    set_pixel_rgb(image, (x, y), (r, g, b))


@export_filter
def mark_middle(image, color, **kwargs):
    x = int(get_height(image) / 2)
    y = int(get_width(image) / 2)
    r, g, b = color
    set_pixel_rgb(image, (x, y), (r, g, b))


@export_tool
def say_hi(image, clicked_coordinate, color, **kwargs):
    x, y = clicked_coordinate
    r, g, b = color
    set_pixel_rgb(image, (x, y), color)
    set_pixel_rgb(image, (x, y - 2), color)
    set_pixel_rgb(image, (x, y - 3), color)
    set_pixel_rgb(image, (x - 2, y + 1), color)
    set_pixel_rgb(image, (x - 2, y), color)
    set_pixel_rgb(image, (x - 2, y - 1), color)
    set_pixel_rgb(image, (x - 2, y - 3), color)
    set_pixel_rgb(image, (x - 3, y - 1), color)
    set_pixel_rgb(image, (x - 4, y + 1), color)
    set_pixel_rgb(image, (x - 4, y), color)
    set_pixel_rgb(image, (x - 4, y - 1), color)
    set_pixel_rgb(image, (x - 2, y - 2), color)
    set_pixel_rgb(image, (x - 4, y - 2), color)
    set_pixel_rgb(image, (x - 4, y - 3), color)


@export_filter
def make_gray(image, color, **kwargs):
    h = int(get_height(image))
    w = int(get_width(image))
    for y in range(h):
        for x in range(w):
            r, g, b = get_pixel_rgb(image, (x, y))
            r = round((r + g + b) // 3)
            g = round((r + g + b) // 3)
            b = round((r + g + b) // 3)
            set_pixel_rgb(image, (x, y), (r, g, b))
