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
from kivy.core.window import Window


def _set_extra(value):
    PythoShopApp._root.extra_input.text = value


def _select_coordinate(x, y):
    _set_extra(str(x) + ", " + str(y))


def _select_color(x, y):
    if PythoShopApp._root.images_tab.current_tab == PythoShopApp._root.primary_tab:
        pass
    img = Image.open(PythoShopApp._bytes)
    r, g, b = img.getpixel((x, y))
    _set_extra(str(r) + ", " + str(g) + ", " + str(b))


def run_manip_function(func, **kwargs):
    print("Running", func)
    if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
        image1 = PythoShopApp._image1
        bytes1 = PythoShopApp._bytes1
        scatter1 = PythoShopApp._root.image1
        image2 = PythoShopApp._image2
        bytes2 = PythoShopApp._bytes2
        scatter2 = PythoShopApp._root.image2
    elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
        image1 = PythoShopApp._image2
        bytes1 = PythoShopApp._bytes2
        scatter1 = PythoShopApp._root.image2
        image2 = PythoShopApp._image1
        bytes2 = PythoShopApp._bytes1
        scatter2 = PythoShopApp._root.image1
    else:
        raise Exception("Neither image tab was selected (which shouldn't be possible)")
    try:
        chosen_color = (
            int(PythoShopApp._root.color_button.background_color[0]*255), 
            int(PythoShopApp._root.color_button.background_color[1]*255), 
            int(PythoShopApp._root.color_button.background_color[2]*255)
        )
        extra_input = PythoShopApp._root.extra_input.text
        bytes1.seek(0)
        img1 = Image.open(bytes1)
        if bytes2:
            bytes2.seek(0)
            img2 = Image.open(bytes2)
        else:
            img2 = None
        result = func(img1, other_image=img2, color=chosen_color, extra=extra_input, **kwargs)
        if result != None:
            if result.__class__ != Image.Image:
                raise Exception("Function", func.__name__, "should have returned an image but instead returned something else")
            if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
                PythoShopApp._bytes1 = BytesIO()
                result.save(PythoShopApp._bytes1, format='png')
                bytes = PythoShopApp._bytes1
            elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
                PythoShopApp._bytes2 = BytesIO()
                result.save(PythoShopApp._bytes2, format='png')
                bytes = PythoShopApp._bytes2
            else:
                raise Exception("No bytes to set")
        else: # No return: assume that the change has been made to the file itself
            bytes = BytesIO()
            if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
                PythoShopApp._bytes1 = bytes
            elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
                PythoShopApp._bytes2 = bytes
            else:
                raise Exception("Neither image tab was selected (which shouldn't be possible)")
            img1.save(bytes, format='png')
        
        bytes.seek(0)
        cimg = CoreImage(bytes, ext='png')
        image1.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        image1.texture.mag_filter = 'nearest'
        image1.texture.min_filter = 'nearest'
    except SyntaxError:
        print("Error: ", func.__name__, "generated an exception")


class FileChooserDialog(Widget):
    def __init__(self, **kwargs):
        super().__init__()
        if 'rootpath' in kwargs:
            self.file_chooser.rootpath = kwargs['rootpath']

    def open(self, file_name):
        print(file_name)
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            image = PythoShopApp._image1
            scatter = PythoShopApp._root.image1
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            image = PythoShopApp._image2
            scatter = PythoShopApp._root.image2
        else:
            raise Exception("Neither image tab was selected (which shouldn't be possible)")

        if image is not None:
            PythoShopApp._root.image1.remove_widget(image)
        PhotoShopWidget._file_chooser_popup.dismiss()

        img = Image.open(file_name[0])
        img = img.convert('RGB')
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            PythoShopApp._bytes1 = BytesIO()
            img.save(PythoShopApp._bytes1, format='png')
            PythoShopApp._bytes1.seek(0)
            cimg = CoreImage(BytesIO(PythoShopApp._bytes1.read()), ext='png')
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            PythoShopApp._bytes2 = BytesIO()
            img.save(PythoShopApp._bytes2, format='png')
            PythoShopApp._bytes2.seek(0)
            cimg = CoreImage(BytesIO(PythoShopApp._bytes2.read()), ext='png')
        else:
            raise Exception("Neither image tab was selected (which shouldn't be possible)")
        
        image = UixImage(fit_mode="contain") # only use this line in first code instance
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            PythoShopApp._image1 = image
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            PythoShopApp._image2 = image
        else:
            raise Exception("Neither image tab was selected (which shouldn't be possible)")

        image.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        image.texture.mag_filter = 'nearest'
        image.texture.min_filter = 'nearest'
        image.size_hint = [None, None]
        image.size = scatter.size
        image.pos = (0, 0)
        scatter.add_widget(image, 100)


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
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab and PythoShopApp._image1:
            img = Image.open(PythoShopApp._bytes1)
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab and PythoShopApp._image2:
            img = Image.open(PythoShopApp._bytes2)
        img.save(os.path.join(os.path.expanduser('~'), "Desktop", "PythoShop " + time.strftime("%Y-%m-%d at %H.%M.%S")+".png"))

    def on_touch_down(self, touch):
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            image = PythoShopApp._image1
            scatter = PythoShopApp._root.image1
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            image = PythoShopApp._image2
            scatter = PythoShopApp._root.image2
        else:
            image = None
            scatter = None
        if image and PythoShopApp._tool_function:
            if not image.parent.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            else:
                lr_space = (image.width - image.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (image.height - image.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                print('lr_space =', lr_space, ', tb_space =', tb_space)
                print("Touch Cords", touch.x, touch.y)
                print('Size of image within ImageView widget:', image.norm_image_size)
                print('ImageView widget:, pos:', image.pos, ', size:', image.size)
                print('image extents in x:', scatter.x + lr_space, image.right - lr_space)
                print('image extents in y:', scatter.y + tb_space, image.top - tb_space)
                pixel_x = touch.x - lr_space - scatter.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - scatter.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                elif pixel_x >= image.norm_image_size[0] or \
                        pixel_y >= image.norm_image_size[1]:
                    print('clicked outside of image\n')
                    return super().on_touch_down(touch)
                else:
                    print('clicked inside image, coords:', pixel_x, pixel_y)

                    # scale coordinates to actual pixels of the Image source
                    actual_x = int(pixel_x * image.texture_size[0] / image.norm_image_size[0])
                    actual_y = (image.texture_size[1] - 1) - int(pixel_y * image.texture_size[1] / image.norm_image_size[1])
                    print('actual pixel coords:', actual_x, actual_y, '\n')
                    # Note: can't call your manip functions "_select_"
                    if PythoShopApp._tool_function.__name__[:8] == "_select_":
                        PythoShopApp._tool_function(actual_x, actual_y)
                    else:
                        run_manip_function(PythoShopApp._tool_function, clicked_x=actual_x, clicked_y=actual_y)
                    return True
        else:
            return super().on_touch_down(touch)
        
    def on_touch_move(self, touch):
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            image = PythoShopApp._image1
            scatter = PythoShopApp._root.image1
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            image = PythoShopApp._image2
            scatter = PythoShopApp._root.image2
        else:
            image = None
            scatter = None

        if image and PythoShopApp._tool_function:
            if not image.parent.collide_point(*touch.pos):
                return super().on_touch_move(touch)
            else:
                lr_space = (image.width - image.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (image.height - image.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                pixel_x = touch.x - lr_space - scatter.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - scatter.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    return super().on_touch_move(touch)
                elif pixel_x >= image.norm_image_size[0] or pixel_y >= image.norm_image_size[1]:
                    return super().on_touch_move(touch)
                else:
                    actual_x = int(pixel_x * image.texture_size[0] / image.norm_image_size[0])
                    actual_y = (image.texture_size[1] - 1) - int(pixel_y * image.texture_size[1] / image.norm_image_size[1])
                    if PythoShopApp._tool_function.__name__[:8] == "_select_":
                        PythoShopApp._tool_function(actual_x, actual_y)
                    else:
                        run_manip_function(PythoShopApp._tool_function, clicked_x=actual_x, clicked_y=actual_y)
                    return True
        else:
            return super().on_touch_move(touch)


class PythoShopApp(App):
    _image1 = None
    _bytes1 = None
    _image2 = None
    _bytes2 = None
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


    def _on_file_drop(self, window, file_path):
        PythoShopApp._root.extra_input.text = file_path


    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
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

            # Selection tools come first
            select_coord_button = Button(text='Select coordinate', size_hint_y=None, height=44)
            select_coord_button.func = _select_coordinate
            select_coord_button.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
            PythoShopApp._tool_dropdown.add_widget(select_coord_button)
            select_color_button = Button(text='Select color', size_hint_y=None, height=44)
            select_color_button.func = _select_color
            select_color_button.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
            PythoShopApp._tool_dropdown.add_widget(select_color_button)

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
                # currently selected tab actually has an image
                if (PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab and PythoShopApp._image1) \
                    or (PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab and PythoShopApp._image2):
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
