import unittest

import tests.test_tool as test_tool


class Test(test_tool.Test, unittest.TestCase):
    manip_func_name = "change_pixel"
    image_sets = [
        ["square"],
        ["wider"],
        ["taller"],
        ["odd"],
        ["even"],
        ["bmpV1"],
    ]
    test_weight = 100
