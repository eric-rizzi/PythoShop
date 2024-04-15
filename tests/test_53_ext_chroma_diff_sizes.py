import unittest
import tests.test_base2 as test_base2


class Extension(test_base2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 5
    image_sets = [
        ("square", "gfish"),
    ]
