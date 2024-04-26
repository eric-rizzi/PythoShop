import unittest

import tests.test_base as test_base


class Extension(test_base.TestBase, unittest.TestCase):
    manip_func_name = "intensify"
    test_weight = 10

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "0.5"})
