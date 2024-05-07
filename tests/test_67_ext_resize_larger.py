import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "resize"
    test_weight = 3

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "3"})
