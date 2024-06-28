import unittest
import tests.testTool as testTool

class Extension(testTool.Test, unittest.TestCase):
    manip_func_name = "draw_x"
    test_weight = 5

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"clicked_coordinate": (10, 10), "extra": "4"})
