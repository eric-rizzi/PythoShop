from PIL import Image
from PhytoShopExports import *

def distance(color1, color2):
    rdiff = abs(color1[0] - color2[0])
    gdiff = abs(color1[1] - color2[1])
    bdiff = abs(color1[2] - color2[2])
    return rdiff + gdiff + bdiff

@export_tool
def change_pixel(img, x=320, y=240, **kwargs):
    px = img.load()
    px[x, y] = (255, 0, 255)

@export_tool
def change_4_pixels(img, x=320, y=240, **kwargs):
    px = img.load()
    px[x, y] = (255, 0, 255)
    px[x+1, y] = (255, 0, 255)
    px[x, y+1] = (255, 0, 255)
    px[x+1, y+1] = (255, 0, 255)

@export_filter
def remove_red(img, **kwargs):
    px = img.load()
    for row in range(img.height):
        for pixel in range(img.width):
            r, g, b = px[pixel, row]
            px[pixel, row] = (0, g, b)

@export_filter
def remove_green(img, **kwargs):
    px = img.load()
    for row in range(img.height):
        for pixel in range(img.width):
            r, g, b = px[pixel, row]
            px[pixel, row] = (r, 0, b)

@export_filter
def remove_blue(img, **kwargs):
    px = img.load()
    for row in range(img.height):
        for pixel in range(img.width):
            r, g, b = px[pixel, row]
            px[pixel, row] = (r, g, 0)

if __name__ == "__main__":
    fname = input("What picturer to use? ")
    image = Image.open(fname)
    # change_pixel(image)
    remove_red(image)
    image.show()
