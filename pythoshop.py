import importlib.util
import os
import time
import typing
from io import BytesIO

from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image as UixImage
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from PIL import Image

from image_manip import *
from tests.config import DEFAULT_STARTING_IMAGE_PATH


class NoImageError(Exception):
    pass


def _set_extra(value) -> None:
    PythoShopApp._root.extra_input.text = value


def _select_coordinate(x: int, y: int) -> None:
    _set_extra(f"{x}, {y}")


def get_current_image() -> tuple:
    if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
        return PythoShopApp._image1, PythoShopApp._bytes1, PythoShopApp._root.image1
    else:
        return PythoShopApp._image2, PythoShopApp._bytes2, PythoShopApp._root.image2


def _select_color(x: int, y: int) -> None:  # sourcery skip: merge-else-if-into-elif
    cimage, cbytes, cscatter = get_current_image()
    if cbytes:
        img = Image.open(cbytes)
        r, g, b = img.getpixel((x, img.height - 1 - y))
        PythoShopApp._color_picker.color = (r / 255, g / 255, b / 255, 1)


def _get_image_bytes(file_name: str) -> BytesIO:
    if os.path.splitext(file_name)[-1].lower() == ".bmp":
        # Load it directly rather than going through Pillow where we might loose some fidelity (e.g. paddding bytes)
        current_bytes = BytesIO()
        current_bytes.write(open(file_name, "rb").read())
    else:
        current_bytes = BytesIO()
        img = Image.open(file_name)
        img = img.convert("RGB")
        img.save(current_bytes, format="bmp")
        img.close()

    return current_bytes


def run_manip_function(func, **kwargs) -> None:
    if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
        cimage = PythoShopApp._image1
        bytes1 = PythoShopApp._bytes1
        bytes2 = PythoShopApp._bytes2
    elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
        cimage = PythoShopApp._image2
        bytes1 = PythoShopApp._bytes2
        bytes2 = PythoShopApp._bytes1
    else:
        raise NoImageError("Neither image tab was selected (which shouldn't be possible)")
    if cimage is None or bytes1 is None:
        raise NoImageError("The currently selected tab doesn't have an image loaded into it")
    try:
        chosen_color = (
            int(PythoShopApp._root.color_button.background_color[0] * 255),
            int(PythoShopApp._root.color_button.background_color[1] * 255),
            int(PythoShopApp._root.color_button.background_color[2] * 255),
        )
        extra_input = PythoShopApp._root.extra_input.text
        bytes1.seek(0)
        if bytes2:
            bytes2.seek(0)
            kwargs["other_image"] = bytes2
        kwargs["color"] = chosen_color
        kwargs["extra"] = extra_input
        result = func(bytes1, **kwargs)
        if result != None:  # Something was returned, make sure it was an image file
            if result.__class__ != BytesIO:
                raise Exception("Function", func.__name__, "should have returned an image but instead returned something else")
            if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
                result_bytes = PythoShopApp._bytes1 = result
            elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
                result_bytes = PythoShopApp._bytes2 = result
            else:
                raise NoImageError("Neither image tab was selected (which shouldn't be possible)")
        else:  # No return: assume that the change has been made to the image itself (img1)
            if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
                PythoShopApp._bytes1 = bytes1
            elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
                PythoShopApp._bytes2 = bytes1
            else:
                raise NoImageError("Neither image tab was selected (which shouldn't be possible)")
            result_bytes = bytes1

        result_bytes.seek(0)
        cimage.texture = CoreImage(result_bytes, ext="bmp").texture
        # to avoid anti-aliassing when zoomed
        cimage.texture.mag_filter = "nearest"
        cimage.texture.min_filter = "nearest"
    except SyntaxError:
        print("Error: ", func.__name__, "generated an exception")


class FileChooserDialog(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        if "rootpath" in kwargs:
            self.file_chooser.rootpath = kwargs["rootpath"]

    def open(self, file_name: list[str]) -> None:
        if not file_name:
            # Early exit if no file selected
            return

        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            image = PythoShopApp._image1
            scatter = PythoShopApp._root.image1
            if image is not None:
                PythoShopApp._root.image1.remove_widget(image)
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            image = PythoShopApp._image2
            scatter = PythoShopApp._root.image2
            if image is not None:
                PythoShopApp._root.image2.remove_widget(image)
        else:
            raise NoImageError("Neither image tab was selected (which shouldn't be possible)")

        PhotoShopWidget._file_chooser_popup.dismiss()

        current_bytes = _get_image_bytes(file_name[0])
        current_bytes.seek(0)
        cimg = CoreImage(current_bytes, ext="bmp")

        uix_image = UixImage(fit_mode="contain")
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab:
            PythoShopApp._bytes1 = current_bytes
            PythoShopApp._image1 = uix_image
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab:
            PythoShopApp._bytes2 = current_bytes
            PythoShopApp._image2 = uix_image
        else:
            raise NoImageError("Neither image tab was selected (which shouldn't be possible)")

        uix_image.texture = cimg.texture
        # to avoid anti-aliassing when we zoom in
        uix_image.texture.mag_filter = "nearest"
        uix_image.texture.min_filter = "nearest"
        uix_image.size_hint = [None, None]
        uix_image.size = scatter.size
        uix_image.pos = (0, 0)
        scatter.add_widget(uix_image, 100)


class PhotoShopWidget(Widget):
    _file_chooser_popup = None

    def toggle_color(self) -> None:
        if PythoShopApp._color_picker.is_visible:
            PythoShopApp._root.children[0].remove_widget(PythoShopApp._color_picker)
            PythoShopApp._color_picker.is_visible = False
            PythoShopApp._root.color_button.text = "Change Color"
        else:
            PythoShopApp._root.children[0].add_widget(PythoShopApp._color_picker)
            PythoShopApp._color_picker.is_visible = True
            PythoShopApp._root.color_button.text = "Set Color"

    def load_image(self) -> None:
        if not PhotoShopWidget._file_chooser_popup:
            PhotoShopWidget._file_chooser_popup = Popup(title="Choose an image", content=FileChooserDialog(rootpath=os.path.expanduser("~")))
        PhotoShopWidget._file_chooser_popup.open()

    def save_image(self) -> None:
        bytes = None
        if PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab and PythoShopApp._image1:
            bytes = PythoShopApp._bytes1
        elif PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab and PythoShopApp._image2:
            bytes = PythoShopApp._bytes2
        if bytes:
            bytes.seek(0)
            new_image_file_name = os.path.join(os.path.expanduser("~"), "Desktop", "PythoShop " + time.strftime("%Y-%m-%d at %H.%M.%S") + ".bmp")
            new_image_file = open(new_image_file_name, "wb")
            new_image_file.write(bytes.read())
            new_image_file.close()

    def apply_tool(self, touch, callback) -> typing.Optional[bool]:
        cimage, cbytes, cscatter = get_current_image()
        if cimage and PythoShopApp._tool_function:
            if not cimage.parent.collide_point(*touch.pos):
                return callback(touch)
            else:
                lr_space = (cimage.width - cimage.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (cimage.height - cimage.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
                pixel_x = touch.x - lr_space - cscatter.x  # x coordinate of touch measured from lower left of actual image
                pixel_y = touch.y - tb_space - cscatter.y  # y coordinate of touch measured from lower left of actual image
                if pixel_x < 0 or pixel_y < 0:
                    return callback(touch)
                elif pixel_x >= cimage.norm_image_size[0] or pixel_y >= cimage.norm_image_size[1]:
                    return callback(touch)
                else:
                    # scale coordinates to actual pixels of the Image source
                    actual_x = int(pixel_x * cimage.texture_size[0] / cimage.norm_image_size[0])
                    actual_y = int(pixel_y * cimage.texture_size[1] / cimage.norm_image_size[1])
                    # Note: can't call your manip functions "_select_"
                    if PythoShopApp._tool_function.__name__[:8] == "_select_":
                        PythoShopApp._tool_function(actual_x, actual_y)
                    else:
                        run_manip_function(PythoShopApp._tool_function, clicked_coordinate=(actual_x, actual_y))
                    return True
        else:
            return super().on_touch_down(touch)

    def on_touch_down(self, touch):
        self.apply_tool(touch, super().on_touch_down)

    def on_touch_move(self, touch):
        self.apply_tool(touch, super().on_touch_move)


class PythoShopApp(App):
    _image1 = None
    _bytes1 = None
    _image2 = None
    _bytes2 = None
    _root = None
    _tool_function = None
    _color_picker = None
    _first_color = True

    def on_color(self, value):
        my_value = value.copy()  # we ignore the alpha chanel
        my_value[3] = 1
        PythoShopApp._root.color_button.background_normal = ""
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
        PythoShopApp._root = PhotoShopWidget()
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
            select_coord_button = Button(text="Select coordinate", size_hint_y=None, height=44)
            select_coord_button.func = _select_coordinate
            select_coord_button.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
            PythoShopApp._tool_dropdown.add_widget(select_coord_button)
            select_color_button = Button(text="Select color", size_hint_y=None, height=44)
            select_color_button.func = _select_color
            select_color_button.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
            PythoShopApp._tool_dropdown.add_widget(select_color_button)

            spec = importlib.util.spec_from_file_location("image_manip", os.getcwd() + "/image_manip.py")
            manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manip_module)  # try to load it to see if we have a syntax error
            for attribute in dir(manip_module):
                thing = getattr(manip_module, attribute)
                if callable(thing) and hasattr(thing, "__wrapped__") and hasattr(thing, "__type__"):
                    if getattr(thing, "__type__") == "filter":
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PythoShopApp._filter_dropdown.select(btn))
                        PythoShopApp._filter_dropdown.add_widget(btn)
                    elif getattr(thing, "__type__") == "tool":
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
                if (PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab and PythoShopApp._image1) or (
                    PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab and PythoShopApp._image2
                ):
                    run_manip_function(btn.func)

            PythoShopApp._filter_dropdown.bind(on_select=select_filter)

            def select_tool(self, btn):
                setattr(PythoShopApp._root.tool_button, "text", btn.text)
                PythoShopApp._tool_function = btn.func

            PythoShopApp._tool_dropdown.bind(on_select=select_tool)
        except SyntaxError:
            print("Error: image_manip.py has a syntax error and can't be executed")

        if os.path.exists(DEFAULT_STARTING_IMAGE_PATH):
            current_bytes = _get_image_bytes(DEFAULT_STARTING_IMAGE_PATH)
            current_bytes.seek(0)
            cimg = CoreImage(current_bytes, ext="bmp")

            # Create a Kivy Image widget for the loaded image
            uix_image = UixImage(fit_mode="contain")
            PythoShopApp._bytes1 = current_bytes
            PythoShopApp._image1 = uix_image

            uix_image.texture = cimg.texture
            # to avoid anti-aliassing when we zoom in
            uix_image.texture.mag_filter = "nearest"
            uix_image.texture.min_filter = "nearest"
            uix_image.size_hint = [None, None]
            uix_image.size = (640, 480)
            uix_image.pos = (0, 0)
            PythoShopApp._root.image1.add_widget(uix_image, 100)

        return PythoShopApp._root


if __name__ == "__main__":
    PythoShopApp().run()
