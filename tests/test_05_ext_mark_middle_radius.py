import unittest
import testTool


class Extension(testTool.Test, unittest.TestCase):
    manip_func_name = "mark_middle"
    image_sets = [
        ["square"],
        ["wider"],
        ["taller"],
        ["odd"],
        ["even"],
        ["bmpV1"],
    ]
    test_weight = 50

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "3"})
