import unittest
import testBase2


class Test(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 33
    image_sets = [
        ("evenC1", "evenC2"),
    ]
