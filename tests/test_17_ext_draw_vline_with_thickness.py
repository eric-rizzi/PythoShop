import unittest
import testTool


class Extension(testTool.Test, unittest.TestCase):
    manip_func_name = "draw_vline"
    test_weight = 5
