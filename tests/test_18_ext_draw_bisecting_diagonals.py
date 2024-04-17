import unittest

import tests.test_base as test_base


class Extension(test_base.TestBase, unittest.TestCase):
    manip_func_name = "draw_bisecting_diagonals"
    test_weight = 10
