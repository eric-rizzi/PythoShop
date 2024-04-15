import unittest

import tests.test_base3 as test_base3


class Extension(test_base3.TestBase3, unittest.TestCase):
    manip_func_name = "shrink"
    test_weight = 15
