import unittest
import tests.test_base as test_base


class Test(test_base.TestBase, unittest.TestCase):
    manip_func_name = "remove_red"
    test_weight = 11
