import unittest

import tests.test_base as test_base


class Extension(test_base.TestBase, unittest.TestCase):
    manip_func_name = "negate_blue"
    test_weight = 3
