import unittest

import tests.test_base as test_base


class Test(test_base.TestBase, unittest.TestCase):
    manip_func_name = "lighten"
    test_weight = 33
