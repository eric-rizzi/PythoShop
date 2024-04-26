import unittest

import tests.test_base as test_base


class Extension(test_base.TestBase, unittest.TestCase):
    manip_func_name = "make_two_tone"
    test_weight = 10

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (255, 255, 0), "extra": "50, 0, 100"})
