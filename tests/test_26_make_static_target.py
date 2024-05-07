import unittest
import testBase
import random

class Test(testBase.TestBase, unittest.TestCase):
    manip_func_name = "make_static"
    test_weight = 20

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "50"})
