import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "draw_centered_hline"
    test_weight = 5
    # Only use images that have an absolute center
    image_sets = [
        ["pad1"],
        ["pad2"],
        ["pad3"],
        ["odd"],
    ]

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "3"})
