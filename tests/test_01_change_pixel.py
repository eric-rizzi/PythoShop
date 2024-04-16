import unittest
import testTool


class Test(testTool.Test, unittest.TestCase):
    manip_func_name = "change_pixel"
    image_sets = [
        ["square"],
        ["wider"],
        ["taller"],
        ["odd"],
        ["even"],
    ]
    test_weight = 100
