import unittest

import tests.test_base3 as test_base3


class Extension(test_base3.TestBase3, unittest.TestCase):
    manip_func_name = "make_line_drawing"
    test_weight = 1

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "3"})
