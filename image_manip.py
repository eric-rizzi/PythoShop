from pythoshop_exports import create_bmp, export_filter, export_tool, get_height, get_pixel_rgb, get_width, set_pixel_rgb


@export_tool
def change_pixel(image, clicked_coordinate, color, **kwargs):
    set_pixel_rgb(image, clicked_coordinate, color)


@export_filter
def mark_middle(image, color, **kwargs):
    middle_y = round(get_height(image) / 2)
    middle_x = round(get_width(image) / 2)
    set_pixel_rgb(image, (middle_x, middle_y), color)


@export_tool
def say_hi(image, clicked_coordinate, color, **kwargs):
    x, y = clicked_coordinate
    set_pixel_rgb(image, (x, y), color)
    set_pixel_rgb(image, (x, y - 2), color)
    set_pixel_rgb(image, (x, y - 3), color)
    set_pixel_rgb(image, (x - 4, y + 1), color)
    set_pixel_rgb(image, (x - 4, y), color)
    set_pixel_rgb(image, (x - 4, y - 1), color)
    set_pixel_rgb(image, (x - 4, y - 2), color)
    set_pixel_rgb(image, (x - 4, y - 3), color)
    set_pixel_rgb(image, (x - 3, y - 1), color)

    set_pixel_rgb(image, (x - 2, y + 1), color)
    set_pixel_rgb(image, (x - 2, y), color)
    set_pixel_rgb(image, (x - 2, y - 1), color)
    set_pixel_rgb(image, (x - 2, y - 2), color)
    set_pixel_rgb(image, (x - 2, y - 3), color)


@export_filter
def mark_four_corners(image, color, **kwargs):
    h = get_height(image) - 1
    w = get_width(image) - 1
    set_pixel_rgb(image, (0, 0), color)
    set_pixel_rgb(image, (0, h), color)
    set_pixel_rgb(image, (w, 0), color)
    set_pixel_rgb(image, (w, h), color)


@export_filter
def mark_middle_with_t(image, color, **kwargs):
    middle_y = round(get_height(image) / 2)
    middle_x = round(get_width(image) / 2)
    set_pixel_rgb(image, (middle_x, middle_y), color)
    for i in range(1, 3):
        set_pixel_rgb(image, (middle_x - i, middle_y), color)
        set_pixel_rgb(image, (middle_x, middle_y - i), color)
        set_pixel_rgb(image, (middle_x + i, middle_y), color)
        set_pixel_rgb(image, (middle_x, middle_y + i), color)


@export_tool
def draw_t(image, clicked_coordinate, color, **kwargs):
    x, y = clicked_coordinate
    set_pixel_rgb(image, (x, y), color)
    for i in range(1, 3):
        set_pixel_rgb(image, (x - i, y), color)
        set_pixel_rgb(image, (x, y - i), color)
        set_pixel_rgb(image, (x + i, y), color)
        set_pixel_rgb(image, (x, y + i), color)


@export_tool
def draw_rainbox(image, clicked_coordinate, color, **kwargs):
    x, y = clicked_coordinate
    set_pixel_rgb(image, (x - 2, y - 2), (255, 0, 0))
    set_pixel_rgb(image, (x - 2, y - 1), (255, 127, 0))
    set_pixel_rgb(image, (x - 1, y), (255, 255, 0))
    set_pixel_rgb(image, (x, y), (0, 255, 0))
    set_pixel_rgb(image, (x + 1, y), (0, 0, 255))
    set_pixel_rgb(image, (x + 2, y - 1), (75, 0, 130))
    set_pixel_rgb(image, (x + 2, y - 2), (148, 0, 211))


@export_tool
def draw_x(image, clicked_coordinate, color, **kwargs):
    x, y = clicked_coordinate
    set_pixel_rgb(image, (x, y), color)
    for i in range(1, 3):
        set_pixel_rgb(image, (x + i, y + i), color)
        set_pixel_rgb(image, (x - i, y - i), color)
        set_pixel_rgb(image, (x + i, y - i), color)
        set_pixel_rgb(image, (x - i, y + i), color)


@export_tool
def draw_hline(image, clicked_coordinate, color, **kwargs) -> None:
    width = get_width(image)
    x, y = clicked_coordinate

    try:
        thickness = int(kwargs["extra"])
    except:
        thickness = 1

    start_row = y - round(thickness / 2)
    for alt_y in range(thickness):
        for x in range(width):
            set_pixel_rgb(image, (x, start_row + alt_y), color)


@export_tool
def draw_vline(image, clicked_coordinate, color, extra, **kwargs) -> None:
    height = get_height(image)
    x, y = clicked_coordinate

    try:
        thickness = int(extra)
    except:
        thickness = 1

    start_column = x - round(thickness / 2)
    for alt_x in range(thickness):
        for y in range(height):
            set_pixel_rgb(image, (start_column + alt_x, y), color)


@export_filter
def remove_red(image, **kwargs) -> None:
    width = get_width(image)
    height = get_height(image)

    for x in range(width):
        for y in range(height):
            r, g, b = get_pixel_rgb(image, (x, y))
            set_pixel_rgb(image, (x, y), (0, g, b))
