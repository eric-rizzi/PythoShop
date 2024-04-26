import unittest

import tests.test_base as test_base


class Test(test_base.TestBase, unittest.TestCase):
    manip_func_name = "say_hi"
    image_sets = [
        ["pad1"],
        ["pad3"],
        ["odd"],
    ]
    test_weight = 10
