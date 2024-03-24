import unittest
import testBase3


class Extension(testBase3.TestBase3, unittest.TestCase):
    manip_func_name = "better_shrink"
    test_weight = 5
