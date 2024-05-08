from PIL import Image
import io

def create_bmp(width, height):
    row_size = width * 3
    row_padding = 0
    if row_size % 4 != 0:
        row_padding = 4 - row_size % 4
        row_size += row_padding
    bmp = io.BytesIO(b'\x42\x4D'+(138 + row_size * height).to_bytes(4, byteorder="little"))
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

def get_info(image):
    '''
    Get information from the header of a BMP file
    :param image: and already-open BMP file with read permission
    :return: tuple containing (in this order):
        the first pixel location
        width
        height
        bits per pixel
        row size
        row padding
    '''
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

filename = "evenC2"
img = open("tests/images/"+filename+".bmp", "rb")
fpp1, w1, h1, bpp1, rs1, pad1 = get_info(img)
new_img = create_bmp(w1, h1)
fpp2, w2, h2, bpp2, rs2, pad2 = get_info(new_img)
img.seek(fpp1)
new_img.seek(fpp2)
new_img.write(img.read())
with open(filename+"_V5.bmp", "wb") as outfile:
    outfile.write(new_img.getbuffer())
img.close()
new_img.close()