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
        PhytoShopApp._bytes.seek(0)
        img = Image.open(PhytoShopApp._bytes)
        func(img, **kwargs)
        PhytoShopApp._bytes = BytesIO()
        img.save(PhytoShopApp._bytes, format='png')
        PhytoShopApp._bytes.seek(0)
        cimg = CoreImage(PhytoShopApp._bytes, ext='png')
        PhytoShopApp._image.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        PhytoShopApp._image.texture.mag_filter = 'nearest'
        PhytoShopApp._image.texture.min_filter = 'nearest'
    except SyntaxError:
        print("Error: ", PhytoShopApp._filter_function.__name__, "generated an exception")


class FileChooserDialog(Widget):
    def __init__(self, **kwargs):
        super().__init__()
        if 'rootpath' in kwargs:
            self.file_chooser.rootpath = kwargs['rootpath']

    def open(self, file_name):
        print(file_name)
        if PhytoShopApp._image is not None:
            PhytoShopApp._root.zoomer.remove_widget(PhytoShopApp._image)
        PhotoShopWidget._file_chooser_popup.dismiss()

        img = Image.open(file_name[0])
        img = img.convert('RGB')
        PhytoShopApp._bytes = BytesIO()
        img.save(PhytoShopApp._bytes, format='png')
        
        PhytoShopApp._bytes.seek(0)
        cimg = CoreImage(BytesIO(PhytoShopApp._bytes.read()), ext='png')
        PhytoShopApp._image = UixImage(fit_mode="contain") # only use this line in first code instance
        PhytoShopApp._image.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        PhytoShopApp._image.texture.mag_filter = 'nearest'
        PhytoShopApp._image.texture.min_filter = 'nearest'
        PhytoShopApp._image.size_hint = [None, None]
        PhytoShopApp._image.size = PhytoShopApp._root.zoomer.size
        PhytoShopApp._image.pos = (0, 0)
        PhytoShopApp._root.zoomer.add_widget(PhytoShopApp._image, 100)


class PhotoShopWidget(Widget):
    _file_chooser_popup = None

    def toggle_color(self):
        if PhytoShopApp._color_picker.is_visible:
            PhytoShopApp._root.children[0].remove_widget(PhytoShopApp._color_picker)
            PhytoShopApp._color_picker.is_visible = False
            PhytoShopApp._root.color_button.text = "Change Color"
        else:
            PhytoShopApp._root.children[0].add_widget(PhytoShopApp._color_picker)
            PhytoShopApp._color_picker.is_visible = True
            PhytoShopApp._root.color_button.text = "Set Color"


    def load_image(self):
        if not PhotoShopWidget._file_chooser_popup:
            PhotoShopWidget._file_chooser_popup = Popup(
                title='Choose an image',
                content=FileChooserDialog(rootpath=os.path.expanduser('~')))
        PhotoShopWidget._file_chooser_popup.open()

    def save_image(self):
        if PhytoShopApp._image:
            img = Image.open(PhytoShopApp._bytes)
            img.save(os.path.join(os.path.expanduser('~'), "Desktop", "PythoShop " + time.strftime("%Y-%m-%d at %H.%M.%S")+".png"))

    def on_touch_down(self, touch):
        if PhytoShopApp._image and PhytoShopApp._tool_function:
            if not PhytoShopApp._image.parent.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            else:
                lr_space = (PhytoShopApp._image.width - PhytoShopApp._image.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (PhytoShopApp._image.height - PhytoShopApp._image.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                print('lr_space =', lr_space, ', tb_space =', tb_space)
                print("Touch Cords", touch.x, touch.y)
                print('Size of image within ImageView widget:', PhytoShopApp._image.norm_image_size)
                print('ImageView widget:, pos:', PhytoShopApp._image.pos, ', size:', PhytoShopApp._image.size)
                print('image extents in x:', PhytoShopApp._root.zoomer.x + lr_space, PhytoShopApp._image.right - lr_space)
                print('image extents in y:', PhytoShopApp._root.zoomer.y + tb_space, PhytoShopApp._image.top - tb_space)
                pixel_x = touch.x - lr_space - PhytoShopApp._root.zoomer.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - PhytoShopApp._root.zoomer.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                elif pixel_x >= PhytoShopApp._image.norm_image_size[0] or \
                        pixel_y >= PhytoShopApp._image.norm_image_size[1]:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                else:
                    print('clicked inside image, coords:', pixel_x, pixel_y)

                    # scale coordinates to actual pixels of the Image source
                    actual_x = int(pixel_x * PhytoShopApp._image.texture_size[0] / PhytoShopApp._image.norm_image_size[0])
                    actual_y = (PhytoShopApp._image.texture_size[1] - 1) - int(pixel_y * PhytoShopApp._image.texture_size[1] / PhytoShopApp._image.norm_image_size[1])
                    print('actual pixel coords:', actual_x, actual_y, '\n')
                    chosen_color = (
                        int(PhytoShopApp._root.color_button.background_color[0]*255), 
                        int(PhytoShopApp._root.color_button.background_color[1]*255), 
                        int(PhytoShopApp._root.color_button.background_color[2]*255)
                    )
                    # chosen_color = (255, 0, 255)
                    run_manip_function(PhytoShopApp._tool_function, x=actual_x, y=actual_y, color=chosen_color)
                    return True
        else:
            return super().on_touch_down(touch)
        

class PhytoShopApp(App):
    _bytes = None
    _image = None
    _root = None
    _tool_function = None
    _color_picker = None
    _first_color = True

    def on_color(instance, value):
        my_value = value.copy()  # we ignore the alpha chanel
        my_value[3] = 1
        PhytoShopApp._root.color_button.background_normal = ''
        PhytoShopApp._root.color_button.background_color = my_value
        if (value[0] + value[1] + value[2]) * value[3] > 1.5:
            PhytoShopApp._root.color_button.color = [0, 0, 0, 1]
        else:
            PhytoShopApp._root.color_button.color = [1, 1, 1, 1]
        if not PhytoShopApp._first_color:
            PhytoShopApp._root.color_button.text = "Set Color"
        else:
            PhytoShopApp._first_color = False

    def build(self):
        PhytoShopApp._root =  PhotoShopWidget()
        # Find the functions that can be run
        try:
            PhytoShopApp._filter_dropdown = DropDown()
            PhytoShopApp._tool_dropdown = DropDown()
            PhytoShopApp._color_dropdown = DropDown()
            PhytoShopApp._color_picker = ColorPicker()
            PhytoShopApp._color_picker.children[0].children[1].children[4].disabled = True  # disable the alpha chanel
            PhytoShopApp._color_picker.bind(color=PhytoShopApp.on_color)
            PhytoShopApp._color_picker.is_visible = False

            spec = importlib.util.spec_from_file_location("ImageManip", os.getcwd() + "/imageManip.py")
            manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manip_module)  # try to load it to see if we have a syntax error
            for attribute in dir(manip_module):
                thing = getattr(manip_module, attribute)
                if callable(thing) and hasattr(thing, '__wrapped__') and hasattr(thing, '__type__'):
                    if getattr(thing, '__type__') == 'filter':
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PhytoShopApp._filter_dropdown.select(btn))
                        PhytoShopApp._filter_dropdown.add_widget(btn)
                    elif getattr(thing, '__type__') == 'tool':
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PhytoShopApp._tool_dropdown.select(btn))
                        PhytoShopApp._tool_dropdown.add_widget(btn)
                    else:
                        print("Error: unrecognized manipulation")
            PhytoShopApp._root.filter_button.bind(on_release=PhytoShopApp._filter_dropdown.open)
            PhytoShopApp._root.tool_button.bind(on_release=PhytoShopApp._tool_dropdown.open)
            def select_filter(self, btn):
                if PhytoShopApp._image:
                    run_manip_function(btn.func)
            PhytoShopApp._filter_dropdown.bind(on_select=select_filter)

            def select_tool(self, btn):
                setattr(PhytoShopApp._root.tool_button, 'text', btn.text)
                PhytoShopApp._tool_function = btn.func
            PhytoShopApp._tool_dropdown.bind(on_select=select_tool)
        except SyntaxError:
            print("Error: ImageManip.py has a syntax error and can't be executed")

        return PhytoShopApp._root


if __name__ == '__main__':
    PhytoShopApp().run()
