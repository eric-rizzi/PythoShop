import unittest

import tests.test_tool as test_tool


class Test(test_tool.Test, unittest.TestCase):
    manip_func_name = "say_hi"
    image_sets = [
        ["pad1"],
        ["pad3"],
        ["odd"],
    ]
    test_weight = 10
