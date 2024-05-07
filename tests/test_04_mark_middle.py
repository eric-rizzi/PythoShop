import unittest
import testBase


class Test(testBase.TestBase, unittest.TestCase):
    manip_func_name = "mark_middle"
    # Only use images that are odd in BOTH dimensions
    image_sets = [
        ["pad1"],
        ["pad3"],
        ["odd"],
    ]
    test_weight = 50
