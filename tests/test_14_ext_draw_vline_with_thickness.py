import unittest

import tests.test_tool as test_tool


class Extension(test_tool.Test, unittest.TestCase):
    manip_func_name = "draw_vline"
    test_weight = 5
