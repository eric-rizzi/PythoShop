from pythoshop_exports import create_bmp, export_filter, export_tool, get_height, get_pixel_rgb, get_width, set_pixel_rgb


@export_tool
def change_pixel(image, clicked_coordinate, **kwargs):
    set_pixel_rgb(image, clicked_coordinate, kwargs["color"])


@export_filter
def mark_middle(image, **kwargs):
    middle_y = round(get_height(image) / 2)
    middle_x = round(get_width(image) / 2)
    set_pixel_rgb(image, (middle_x, middle_y), kwargs["color"])


@export_filter
def draw_hline(image, **kwargs) -> None:
    width = get_width(image)
    x, y = kwargs["clicked_coordinate"]

    try:
        thickness = int(kwargs["extra"])
    except:
        thickness = 1

    start_row = y - round(thickness / 2)
    for alt_y in range(thickness):
        for x in range(width):
            set_pixel_rgb(image, (x, start_row + alt_y), kwargs["color"])


@export_filter
def draw_vline(image, **kwargs) -> None:
    height = get_height(image)
    x, y = kwargs["clicked_coordinate"]

    try:
        thickness = int(kwargs["extra"])
    except:
        thickness = 1

    start_column = x - round(thickness / 2)
    for alt_x in range(thickness):
        for y in range(height):
            set_pixel_rgb(image, (start_column + alt_x, y), kwargs["color"])


@export_filter
def remove_red(image, **kwargs) -> None:
    width = get_width(image)
    height = get_height(image)

    for x in range(width):
        for y in range(height):
            r, g, b = get_pixel_rgb(image, (x, y))
            set_pixel_rgb(image, (x, y), (0, g, b))
