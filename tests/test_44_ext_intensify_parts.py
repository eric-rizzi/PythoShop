import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "intensify"
    test_weight = 5

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "1.0, 0.0, 1.0"})
