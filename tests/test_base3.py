import io
import platform
import random
import signal
import tempfile

import tests.config as config
import tests.test_base as test_base


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


class TestBase3(test_base.TestBase):
    """
    The functions that this tests take one image and makes a new
    image which gets returned from the function
    """

    num_image_parameters = 1

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters = self.__class__.test_parameters.copy()

    def test_images(self):
        with TestTimeout(10):
            if self.image_sets is None:
                self.image_sets = list([file_name] for file_name in config.FILE_NAMES)
            for image_set in self.image_sets:
                image = image_set[0]
                with self.subTest(i=image):
                    random.seed(0)  # make it predictably random
                    image1_file_name = image + ".bmp"
                    test_file_name = self.manip_func_name + self.get_parameter_str() + "-" + image + ".bmp"
                    static_manip_func = getattr(self.manip_module, self.manip_func_name)
                    with tempfile.TemporaryFile() as image1:
                        image1.write(self.original_images[image1_file_name])
                        try:
                            result = static_manip_func(image1, **self.test_parameters)
                        except Exception as e:
                            self.assertTrue(False, "Running on " + image1_file_name + " casused an exception: " + str(e))
                        first_pixel_index = int.from_bytes(self.solution_images[test_file_name][10:14], "little")
                        width = int.from_bytes(self.solution_images[test_file_name][18:22], "little")
                        height = int.from_bytes(self.solution_images[test_file_name][22:26], "little")
                        row_size = width * 3
                        row_padding = 0
                        if row_size % 4 != 0:
                            row_padding = 4 - row_size % 4
                            row_size += row_padding
                        self.assertTrue(result is not None, "Your function didn't return the resulting image")
                        self.assertTrue(type(result) == io.BytesIO)
                        result.seek(0)
                        header = result.read(first_pixel_index)
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
                                actual_b, actual_g, actual_r = result.read(3)
                                if actual_b != correct_b or actual_g != correct_g or actual_r != correct_r:
                                    original1_b, original1_g, original1_r = self.original_images[image1_file_name][pixel_index : pixel_index + 3]
                                    self.assertTrue(
                                        False,
                                        "Pixel at ("
                                        + str(pixel)
                                        + ", "
                                        + str(row)
                                        + ") is incorrect. \nOriginal was "
                                        + str([original1_b, original1_g, original1_r])
                                        + "\nIt should be "
                                        + str([correct_b, correct_g, correct_r])
                                        + "\nBut actually "
                                        + str([actual_b, actual_g, actual_r]),
                                    )
                            result.read(row_padding)
