import unittest

import tests.test_base3 as test_base3


class Test(test_base3.TestBase3, unittest.TestCase):
    manip_func_name = "make_line_drawing"
    test_weight = 25
