import unittest

import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "mark_middle"
    # Only use images that are odd in BOTH dimensions
    image_sets = [
        ["pad1"],
        ["pad3"],
        ["odd"],
    ]
    test_weight = 1

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "3"})
