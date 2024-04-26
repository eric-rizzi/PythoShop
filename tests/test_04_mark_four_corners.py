import unittest

import tests.test_base as test_base


class Test(test_base.TestBase, unittest.TestCase):
    manip_func_name = "mark_four_corners"
    image_sets = [
        ["pad1"],
        ["pad3"],
        ["odd"],
    ]
    test_weight = 20
