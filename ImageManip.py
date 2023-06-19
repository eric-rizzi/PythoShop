from PIL import Image


# img = Image.open("pokeball.jpg")
# px = img.load()
# # Show the first pixel
# print(px[0, 0])
# # Change the first pixel
# px[0, 0] = (255, 0, 255)

def change_pixel(img, x=320, y=240, **kwargs):
    px = img.load()
    px[x, y] = (255, 0, 255)

def remove_red(img, **kwargs):
    px = img.load()
    for row in range(img.height):
        for pixel in range(img.width):
            r, g, b = px[pixel, row]
            px[pixel, row] = (0, g, b)

if __name__ == "__main__":
    fname = input("What picturer to use? ")
    image = Image.open(fname)
    # change_pixel(image)
    remove_red(image)
    image.show()
