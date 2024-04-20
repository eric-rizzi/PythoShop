import unittest

import tests.test_tool as test_tool


class Extension(test_tool.Test, unittest.TestCase):
    manip_func_name = "draw_hline"
    test_weight = 5

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "4"})
