import unittest
import testBase2


class Extension(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "blend_gradual_horizontal"
    test_weight = 5
    image_sets = [
        ("evenB1", "evenB2"),
        ("oddB1", "oddB2"),  # requires padding
    ]
