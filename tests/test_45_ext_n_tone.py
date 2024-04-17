import unittest

import tests.test_base as test_base


class Extension(test_base.TestBase, unittest.TestCase):
    manip_func_name = "make_n_tone"
    test_weight = 20

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "6"})
