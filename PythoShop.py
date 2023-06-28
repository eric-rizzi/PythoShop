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
from kivy.uix.colorpicker import ColorPicker

def run_manip_function(func, **kwargs):
    print("Running", func)
    try:
        PythoShopApp._bytes.seek(0)
        img = Image.open(PythoShopApp._bytes)
        func(img, **kwargs)
        PythoShopApp._bytes = BytesIO()
        img.save(PythoShopApp._bytes, format='png')
        PythoShopApp._bytes.seek(0)
        cimg = CoreImage(PythoShopApp._bytes, ext='png')
        PythoShopApp._image.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        PythoShopApp._image.texture.mag_filter = 'nearest'
        PythoShopApp._image.texture.min_filter = 'nearest'
    except SyntaxError:
        print("Error: ", PythoShopApp._filter_function.__name__, "generated an exception")


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
        PythoShopApp._image.size = PythoShopApp._root.zoomer.size
        PythoShopApp._image.pos = (0, 0)
        PythoShopApp._root.zoomer.add_widget(PythoShopApp._image, 100)


class PhotoShopWidget(Widget):
    _file_chooser_popup = None

    def toggle_color(self):
        if PythoShopApp._color_picker.is_visible:
            PythoShopApp._root.children[0].remove_widget(PythoShopApp._color_picker)
            PythoShopApp._color_picker.is_visible = False
            PythoShopApp._root.color_button.text = "Change Color"
        else:
            PythoShopApp._root.children[0].add_widget(PythoShopApp._color_picker)
            PythoShopApp._color_picker.is_visible = True
            PythoShopApp._root.color_button.text = "Set Color"


    def load_image(self):
        if not PhotoShopWidget._file_chooser_popup:
            PhotoShopWidget._file_chooser_popup = Popup(
                title='Choose an image',
                content=FileChooserDialog(rootpath=os.path.expanduser('~')))
        PhotoShopWidget._file_chooser_popup.open()

    def save_image(self):
        if PythoShopApp._image:
            img = Image.open(PythoShopApp._bytes)
            img.save(os.path.join(os.path.expanduser('~'), "Desktop", "PythoShop " + time.strftime("%Y-%m-%d at %H.%M.%S")+".png"))

    def on_touch_down(self, touch):
        if PythoShopApp._image and PythoShopApp._tool_function:
            if not PythoShopApp._image.parent.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            else:
                lr_space = (PythoShopApp._image.width - PythoShopApp._image.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (PythoShopApp._image.height - PythoShopApp._image.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                print('lr_space =', lr_space, ', tb_space =', tb_space)
                print("Touch Cords", touch.x, touch.y)
                print('Size of image within ImageView widget:', PythoShopApp._image.norm_image_size)
                print('ImageView widget:, pos:', PythoShopApp._image.pos, ', size:', PythoShopApp._image.size)
                print('image extents in x:', PythoShopApp._root.zoomer.x + lr_space, PythoShopApp._image.right - lr_space)
                print('image extents in y:', PythoShopApp._root.zoomer.y + tb_space, PythoShopApp._image.top - tb_space)
                pixel_x = touch.x - lr_space - PythoShopApp._root.zoomer.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - PythoShopApp._root.zoomer.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                elif pixel_x >= PythoShopApp._image.norm_image_size[0] or \
                        pixel_y >= PythoShopApp._image.norm_image_size[1]:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                else:
                    print('clicked inside image, coords:', pixel_x, pixel_y)

                    # scale coordinates to actual pixels of the Image source
                    actual_x = int(pixel_x * PythoShopApp._image.texture_size[0] / PythoShopApp._image.norm_image_size[0])
                    actual_y = (PythoShopApp._image.texture_size[1] - 1) - int(pixel_y * PythoShopApp._image.texture_size[1] / PythoShopApp._image.norm_image_size[1])
                    print('actual pixel coords:', actual_x, actual_y, '\n')
                    chosen_color = (
                        int(PythoShopApp._root.color_button.background_color[0]*255), 
                        int(PythoShopApp._root.color_button.background_color[1]*255), 
                        int(PythoShopApp._root.color_button.background_color[2]*255)
                    )
                    # chosen_color = (255, 0, 255)
                    run_manip_function(PythoShopApp._tool_function, x=actual_x, y=actual_y, color=chosen_color)
                    return True
        else:
            return super().on_touch_down(touch)
        

class PythoShopApp(App):
    _bytes = None
    _image = None
    _root = None
    _tool_function = None
    _color_picker = None
    _first_color = True

    def on_color(instance, value):
        my_value = value.copy()  # we ignore the alpha chanel
        my_value[3] = 1
        PythoShopApp._root.color_button.background_normal = ''
        PythoShopApp._root.color_button.background_color = my_value
        if (value[0] + value[1] + value[2]) * value[3] > 1.5:
            PythoShopApp._root.color_button.color = [0, 0, 0, 1]
        else:
            PythoShopApp._root.color_button.color = [1, 1, 1, 1]
        if not PythoShopApp._first_color:
            PythoShopApp._root.color_button.text = "Set Color"
        else:
            PythoShopApp._first_color = False

    def build(self):
        PythoShopApp._root =  PhotoShopWidget()
        # Find the functions that can be run
        try:
            PythoShopApp._filter_dropdown = DropDown()
            PythoShopApp._tool_dropdown = DropDown()
            PythoShopApp._color_dropdown = DropDown()
            PythoShopApp._color_picker = ColorPicker()
            PythoShopApp._color_picker.children[0].children[1].children[4].disabled = True  # disable the alpha chanel
            PythoShopApp._color_picker.bind(color=PythoShopApp.on_color)
            PythoShopApp._color_picker.is_visible = False

            spec = importlib.util.spec_from_file_location("ImageManip", os.getcwd() + "/imageManip.py")
            manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manip_module)  # try to load it to see if we have a syntax error
            for attribute in dir(manip_module):
                thing = getattr(manip_module, attribute)
                if callable(thing) and hasattr(thing, '__wrapped__') and hasattr(thing, '__type__'):
                    if getattr(thing, '__type__') == 'filter':
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PythoShopApp._filter_dropdown.select(btn))
                        PythoShopApp._filter_dropdown.add_widget(btn)
                    elif getattr(thing, '__type__') == 'tool':
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
                        PythoShopApp._tool_dropdown.add_widget(btn)
                    else:
                        print("Error: unrecognized manipulation")
            PythoShopApp._root.filter_button.bind(on_release=PythoShopApp._filter_dropdown.open)
            PythoShopApp._root.tool_button.bind(on_release=PythoShopApp._tool_dropdown.open)
            def select_filter(self, btn):
                if PythoShopApp._image:
                    run_manip_function(btn.func)
            PythoShopApp._filter_dropdown.bind(on_select=select_filter)

            def select_tool(self, btn):
                setattr(PythoShopApp._root.tool_button, 'text', btn.text)
                PythoShopApp._tool_function = btn.func
            PythoShopApp._tool_dropdown.bind(on_select=select_tool)
        except SyntaxError:
            print("Error: ImageManip.py has a syntax error and can't be executed")

        return PythoShopApp._root


if __name__ == '__main__':
    PythoShopApp().run()
