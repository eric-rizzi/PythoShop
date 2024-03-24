import testBase


class Test(testBase.TestBase):
    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters = self.__class__.test_parameters.copy()
        self.__class__.test_parameters.update({"clicked_coordinate": (4, 5)})
