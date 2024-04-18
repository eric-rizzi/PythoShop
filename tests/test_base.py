import importlib.util
import inspect
import os
import pickle
import platform
import random
import signal
import tempfile
import typing
import unittest

import tests.config as config


class TestTimeoutException(Exception):
    pass


class TestTimeout:
    def __init__(self, seconds, error_message=None):
        if error_message is None:
            error_message = "test timed out after {}s.".format(seconds)
            self.seconds = seconds
            self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TestTimeoutException(self.error_message)

    def __enter__(self):
        if not "Windows" in platform.system():
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not "Windows" in platform.system():
            signal.alarm(0)


class TestBase:
    original_images: dict[str, bytes] = {}
    solution_images: dict[str, bytes] = {}
    test_parameters = {
        "color": (238, 0, 119),
        "extra": "extra parameters...",
    }
    manip_func_name: typing.Optional[str] = None
    manip_func: typing.Optional[str] = None
    test_weight = 0
    image_sets: typing.Optional[list[list[str]]] = None
    manip_module = None
    num_image_parameters = 1

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters = self.__class__.test_parameters.copy()
        if self.image_sets is None:
            self.image_sets = list([file_name] for file_name in config.FILE_NAMES)

    @classmethod
    def get_parameter_str(cls):
        parameter_str = ""
        for parameter_name, parameter_value in cls.test_parameters.items():
            parameter_str += "_" + parameter_name + "_" + str(parameter_value)
        return parameter_str

    @classmethod
    def setUpClass(cls):
        pickled_originals = open(config.TEST_ORIGINALS_PICKLE_FILE_NAME, "rb")
        cls.original_images = pickle.load(pickled_originals)
        pickled_originals.close()

        try:
            spec = importlib.util.spec_from_file_location("image_manip.py", "image_manip.py")

            cls.manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.manip_module)
            if cls.manip_func_name in dir(cls.manip_module):
                cls.manip_func = getattr(cls.manip_module, cls.manip_func_name)
            else:
                raise unittest.SkipTest(cls.__module__ + ": function " + cls.manip_func_name + "() is not available to test")
        except SyntaxError:
            raise unittest.SkipTest(cls.__module__ + ": image_manip.py has a syntax error and can't be tested")

        positional_args = inspect.getfullargspec(cls.manip_func.__wrapped__).args.copy()
        # starting from the end, remove all the args that are handled by kwargs so we're left with just positional args
        while positional_args[-1] in cls.test_parameters:
            positional_args = positional_args[:-1]
        # what should be left is just the image parameters
        if len(positional_args) < cls.num_image_parameters:
            raise unittest.SkipTest(
                cls.__module__
                + ": function "
                + cls.manip_func_name
                + "() does not take "
                + str(len(cls.test_parameters) + cls.num_image_parameters)
                + " parameters."
            )

        pickled_solutions_file_name = cls.__module__ + ".pickle"
        pickled_solutions_file_path = os.path.join(config.EXPECTED_OUTPUT_IMAGE_FOLDER, pickled_solutions_file_name)
        pickled_solutions = open(pickled_solutions_file_path, "rb")
        cls.solution_images = pickle.load(pickled_solutions)
        pickled_solutions.close()

    def test_images(self):
        with TestTimeout(10):
            for image_set in self.image_sets:
                image = image_set[0]
                with self.subTest(i=image_set):
                    random.seed(0)  # make it predictably random
                    orig_file_name = image + ".bmp"
                    test_file_name = self.manip_func_name + self.get_parameter_str() + "-" + image + ".bmp"
                    static_manip_func = getattr(self.manip_module, self.manip_func_name)
                    with tempfile.TemporaryFile() as image_file:
                        image_file.write(self.original_images[orig_file_name])
                        try:
                            static_manip_func(image_file, **self.test_parameters)
                        except Exception as e:
                            self.assertTrue(False, "Running on " + orig_file_name + " caused an exception: " + str(e))
                        first_pixel_index = int.from_bytes(self.solution_images[test_file_name][10:14], "little")
                        width = int.from_bytes(self.solution_images[test_file_name][18:22], "little")
                        height = int.from_bytes(self.solution_images[test_file_name][22:26], "little")
                        row_size = width * 3
                        row_padding = 0
                        if row_size % 4 != 0:
                            row_padding = 4 - row_size % 4
                            row_size += row_padding
                        image_file.seek(0)
                        header = image_file.read(first_pixel_index)
                        self.assertTrue(
                            header == self.solution_images[test_file_name][:first_pixel_index],
                            "The header information is incorrect.\n  Should be: "
                            + self.solution_images[test_file_name][:first_pixel_index].hex()
                            + "\n   Actually: "
                            + header.hex(),
                        )
                        for row in range(height):
                            row_index = first_pixel_index + row_size * row
                            for pixel in range(width):
                                pixel_index = row_index + pixel * 3
                                correct_b, correct_g, correct_r = self.solution_images[test_file_name][pixel_index : pixel_index + 3]
                                actual_b, actual_g, actual_r = image_file.read(3)
                                if actual_b != correct_b or actual_g != correct_g or actual_r != correct_r:
                                    original_b, original_g, original_r = self.original_images[orig_file_name][pixel_index : pixel_index + 3]
                                    self.assertTrue(
                                        False,
                                        "Pixel at ("
                                        + str(pixel)
                                        + ", "
                                        + str(row)
                                        + ") is incorrect. \nOriginal was "
                                        + str([original_b, original_g, original_r])
                                        + "\nIt should be "
                                        + str([correct_b, correct_g, correct_r])
                                        + "\nBut actually "
                                        + str([actual_b, actual_g, actual_r]),
                                    )
                            image_file.read(row_padding)
