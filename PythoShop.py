from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as UixImage
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
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
import time


class FileChooserDialog(Widget):
    def __init__(self, **kwargs):
        super().__init__()
        if 'rootpath' in kwargs:
            self.file_chooser.rootpath = kwargs['rootpath']

    def open(self, file_name):
        print(file_name)
        if PythoShopApp._image is not None:
            PythoShopApp._root.zoomer.remove_widget(PythoShopApp._image)
        PhotoShopWidget._file_chooser_popup.dismiss()

        img = Image.open(file_name[0])
        img = img.convert('RGB')
        PythoShopApp._bytes = BytesIO()
        img.save(PythoShopApp._bytes, format='png')
        
        PythoShopApp._bytes.seek(0)
        cimg = CoreImage(BytesIO(PythoShopApp._bytes.read()), ext='png')
        PythoShopApp._image = UixImage(fit_mode="contain") # only use this line in first code instance
        PythoShopApp._image.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        PythoShopApp._image.texture.mag_filter = 'nearest'
        PythoShopApp._image.texture.min_filter = 'nearest'
        PythoShopApp._image.size_hint = [None, None]
        PythoShopApp._image.size = PythoShopApp._root.size
        # PythoShopApp._image.pos = (0, 0)
        PythoShopApp._root.zoomer.add_widget(PythoShopApp._image)


class CustomDropDown(DropDown):
    pass


class PhotoShopWidget(Widget):
    _file_chooser_popup = None

    def load_image(self):
        PhotoShopWidget._file_chooser_popup = Popup(
            title='Choose an image',
            content=FileChooserDialog(rootpath=os.path.expanduser('~')))
        PhotoShopWidget._file_chooser_popup.open()

    def save_image(self):
        if PythoShopApp._image:
            img = Image.open(PythoShopApp._bytes)
            img.save(os.path.join(os.path.expanduser('~'), "Desktop", "PythoShop " + time.strftime("%Y-%m-%d at %H.%M.%S")+".png"))


    def run_code(self, fname, **kwargs):
        print("Running", fname)
        if PythoShopApp._image:
            # Find the function to be run
            try:
                spec = importlib.util.spec_from_file_location("imageManip", os.getcwd() + "/imageManip.py")
                manip_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(manip_module)
                if fname in dir(manip_module):
                    manip_func = getattr(manip_module, fname)
                    PythoShopApp._bytes.seek(0)
                    img = Image.open(PythoShopApp._bytes)
                    manip_func(img, **kwargs)
                    PythoShopApp._bytes = BytesIO()
                    img.save(PythoShopApp._bytes, format='png')
                    PythoShopApp._bytes.seek(0)
                    cimg = CoreImage(PythoShopApp._bytes, ext='png')
                    PythoShopApp._image.texture = cimg.texture
                    # to avoid anti-aliassing when we zoom in
                    PythoShopApp._image.texture.mag_filter = 'nearest'
                    PythoShopApp._image.texture.min_filter = 'nearest'
                else:
                    print("Function " + fname + "() is not available to test")
            except SyntaxError:
                print("imageManip.py has a syntax error and can't be executed")

    def on_touch_down(self, touch):
        if PythoShopApp._image:
            if not PythoShopApp._image.parent.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            else:
                lr_space = (PythoShopApp._image.width - PythoShopApp._image.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (PythoShopApp._image.height - PythoShopApp._image.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                print('lr_space =', lr_space, ', tb_space =', tb_space)
                print("Touch Cords", touch.x, touch.y)
                print('Size of image within ImageView widget:', PythoShopApp._image.norm_image_size)
                print('ImageView widget:, pos:', PythoShopApp._image.pos, ', size:', PythoShopApp._image.size)
                print('image extents in x:', PythoShopApp._image.x + lr_space, PythoShopApp._image.right - lr_space)
                print('image extents in y:', PythoShopApp._image.y + tb_space, PythoShopApp._image.top - tb_space)
                pixel_x = touch.x - lr_space - PythoShopApp._image.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - PythoShopApp._image.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                elif pixel_x > PythoShopApp._image.norm_image_size[0] or \
                        pixel_y > PythoShopApp._image.norm_image_size[1]:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                else:
                    print('clicked inside image, coords:', pixel_x, pixel_y)

                    # scale coordinates to actual pixels of the Image source
                    actual_x = round(pixel_x * PythoShopApp._image.texture_size[0] / PythoShopApp._image.norm_image_size[0])
                    actual_y = PythoShopApp._image.texture_size[1] - round(pixel_y * PythoShopApp._image.texture_size[1] / PythoShopApp._image.norm_image_size[1])
                    print('actual pixel coords:', actual_x, actual_y, '\n')
                    PhotoShopWidget.run_code(None, "change_pixel", x=actual_x, y=actual_y)
                    return True
        else:
            return super().on_touch_down(touch)
        

class PythoShopApp(App):
    _bytes = None
    _image = None
    _root = None

    def build(self):
        PythoShopApp._root =  PhotoShopWidget()
        return PythoShopApp._root


if __name__ == '__main__':
    PythoShopApp().run()
