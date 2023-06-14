from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as UixImage
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.graphics import Color
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from ImageManip import *
import os
from random import random
import importlib.util
import inspect


class FileChooserDialog(Widget):
    def __init__(self, **kwargs):
        super().__init__()
        if 'rootpath' in kwargs:
            self.file_chooser.rootpath = kwargs['rootpath']

    def open(self, file_name):
        print(file_name)
        if PhotoshopApp._image is not None:
            PhotoshopApp._root.zoomer.remove_widget(PhotoshopApp._image)
        PhotoShopWidget._file_chooser_popup.dismiss()

        img = Image.open(file_name[0])
        PhotoshopApp._bytes = BytesIO()
        img.save(PhotoshopApp._bytes, format='png')
        
        PhotoshopApp._bytes.seek(0)
        cimg = CoreImage(BytesIO(PhotoshopApp._bytes.read()), ext='png')
        PhotoshopApp._image = UixImage(fit_mode="contain") # only use this line in first code instance
        PhotoshopApp._image.texture = cimg.texture
        PhotoshopApp._image.size_hint = [None, None]
        PhotoshopApp._image.size = PhotoshopApp._root.size
        # PhotoshopApp._image.pos = (0, 0)
        PhotoshopApp._root.zoomer.add_widget(PhotoshopApp._image)


class PhotoShopWidget(Widget):
    _file_chooser_popup = None

    def load_image(self):
        PhotoShopWidget._file_chooser_popup = Popup(
            title='Choose an image',
            content=FileChooserDialog(rootpath=os.path.expanduser('~')))
        PhotoShopWidget._file_chooser_popup.open()

    def run_code(self, fname, **kwargs):
        print("Running", fname)
        # Find the function to be run
        try:
            spec = importlib.util.spec_from_file_location("imageManip", os.getcwd() + "/imageManip.py")
            manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manip_module)
            if fname in dir(manip_module):
                manip_func = getattr(manip_module, fname)
                PhotoshopApp._bytes.seek(0)
                img = Image.open(PhotoshopApp._bytes)
                manip_func(img, **kwargs)
                PhotoshopApp._bytes = BytesIO()
                img.save(PhotoshopApp._bytes, format='png')
                PhotoshopApp._bytes.seek(0)
                cimg = CoreImage(PhotoshopApp._bytes, ext='png')
                PhotoshopApp._image.texture = cimg.texture
                # to avoid anti-aliassing when we zoom in
                PhotoshopApp._image.texture.mag_filter = 'nearest'
                PhotoshopApp._image.texture.min_filter = 'nearest'
            else:
                print("Function " + fname + "() is not available to test")
        except SyntaxError:
            print("imageManip.py has a syntax error and can't be executed")

    def on_touch_down(self, touch):
        if PhotoshopApp._image:
            if not PhotoshopApp._image.parent.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            else:
                lr_space = (PhotoshopApp._image.width - PhotoshopApp._image.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (PhotoshopApp._image.height - PhotoshopApp._image.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                print('lr_space =', lr_space, ', tb_space =', tb_space)
                print("Touch Cords", touch.x, touch.y)
                print('Size of image within ImageView widget:', PhotoshopApp._image.norm_image_size)
                print('ImageView widget:, pos:', PhotoshopApp._image.pos, ', size:', PhotoshopApp._image.size)
                print('image extents in x:', PhotoshopApp._image.x + lr_space, PhotoshopApp._image.right - lr_space)
                print('image extents in y:', PhotoshopApp._image.y + tb_space, PhotoshopApp._image.top - tb_space)
                pixel_x = touch.x - lr_space - PhotoshopApp._image.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - PhotoshopApp._image.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                elif pixel_x > PhotoshopApp._image.norm_image_size[0] or \
                        pixel_y > PhotoshopApp._image.norm_image_size[1]:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                else:
                    print('clicked inside image, coords:', pixel_x, pixel_y)

                    # scale coordinates to actual pixels of the Image source
                    actual_x = int(pixel_x * PhotoshopApp._image.texture_size[0] / PhotoshopApp._image.norm_image_size[0])
                    actual_y = PhotoshopApp._image.texture_size[1] - int(pixel_y * PhotoshopApp._image.texture_size[1] / PhotoshopApp._image.norm_image_size[1])
                    print('actual pixel coords:', actual_x, actual_y, '\n')
                    PhotoShopWidget.run_code(None, "change_pixel", x=actual_x, y=actual_y)
                    return True
        else:
            return super().on_touch_down(touch)
        

class PhotoshopApp(App):
    _bytes = None
    _image = None
    _root = None

    def build(self):
        PhotoshopApp._root =  PhotoShopWidget()
        # PhotoshopApp._image = Image(source="pokeball.png")
        # PhotoshopApp._root.add_widget(PhotoshopApp._image)
        return PhotoshopApp._root


if __name__ == '__main__':
    PhotoshopApp().run()
