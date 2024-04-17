import unittest

import tests.test_base2 as test_base2


class Test(test_base2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 33
    image_sets = [
        ["evenC1", "evenC2"],
        ["oddC1", "oddC2"],  # requires padding
    ]
