import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "draw_gray"
    test_weight = 15

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"clicked_coordinate": (12, 18), "extra": "8"})
