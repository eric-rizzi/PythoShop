import unittest
import sys
import os
import subprocess


def dummyInput(prompt=None):
    raise RuntimeError("You should not be calling the input function within your manipulation functions (only in __main__)")


def dummyRun(args, *, stdin=None, input=None, stdout=None, stderr=None, capture_output=False, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None, text=None, env=None, universal_newlines=None):
    raise RuntimeError("You should not be calling the subprocess.run function within your manipulation functions (only in __main__)")


sys.modules['subprocess'].run = dummyRun
sys.modules['builtins'].input = dummyInput


class TestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.separator1 = "\n" + self.separator1
        self.points_total = 0
        self.tests = []

    def addPoints(self, test):
        assert test.test_weight != 0, "Test " + str(test) + " has zero weight"
        assert type(test).__name__ == "Test" or type(test).__name__ == "Extension", "Test " + str(test) + " is not named \"Test\" or \"Extension\""
        if type(test).__name__ == "Test":
            self.points_total += test.test_weight

    def startTest(self, test):
        print(".", end="", flush=True)
        self.addPoints(test)
        self.tests.append(test)
        super().startTest(test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        # What a hack but I can't see any other way to get this
        skipped_module_name = test.description[test.description.find("(")+1: test.description.find(".")]
        skipped_class_name = test.description[test.description.find(".")+1: test.description.find(")")]
        print("#", end="", flush=True)
        if skipped_class_name == "Test":
            skipped_module = __import__(skipped_module_name)
            if skipped_class_name in dir(skipped_module):
                skipped_class = getattr(skipped_module, skipped_class_name)
                self.points_total += skipped_class.test_weight



if __name__ == '__main__':
    testSuite = unittest.defaultTestLoader.discover(".")
    testProgram = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    testProgram.resultclass = TestResult
    testResults = testProgram.run(testSuite)
    print("")
    print("Grade Breakdown")
    print("======================================================================")
    points_total = 0
    points_earned = 0
    tests_passed = []
    tests_partial = []
    tests_failed = []
    for test in testResults.tests:
        num_sub_tests = len(test.image_sets)
        sub_failures = [x for x in testResults.failures if x[0].test_case == test]
        num_sub_failures = len(sub_failures)
        num_sub_success = num_sub_tests - num_sub_failures
        percentage = 0
        if num_sub_failures == 0:
            tests_passed.append(test.__module__)
            percentage = 1.0
        elif num_sub_success > 0:
            tests_partial.append(test.__module__)
            # Get ~80% if passed at least one
            percentage = 0.75 + 0.25 * num_sub_success / num_sub_tests
        else:
            tests_failed.append(test.__module__)
            percentage = 0
        percentage_str = str(round(percentage * 100))
        points = percentage * test.test_weight
        points_earned += points
        print(" " * (3 - len(percentage_str)) + percentage_str + "% " + str(test.__module__) + " (" + str(round(points, 1)) + " points)")

    points_total = int(1.15 * testResults.points_total)
    for skip in testResults.skipped:
        print("Skipped " + skip[1])

    print("")
    print("Grade Summary")
    print("======================================================================")
    print("  Total Points: " + str(points_total))
    print(" Points Earned: " + str(round(points_earned)))
    if points_total > 0:  # otherwise get a divide by zero
        print("Grade (approx): " + str(round(100 * points_earned / points_total)))
    else:
        print("Grade (approx): 0")
