import unittest
import testTool


class Extension(testTool.Test, unittest.TestCase):
    manip_func_name = "draw_vline"
    test_weight = 10

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"clicked_coordinate": (13, 0)})
