import unittest

import tests.test_base as test_base


class Extension(test_base.TestBase, unittest.TestCase):
    manip_func_name = "draw_centered_hline"
    test_weight = 5
    # Only use images that have an absolute center
    image_sets = [
        ["pad1"],
        ["pad2"],
        ["pad3"],
        ["odd"],
    ]
