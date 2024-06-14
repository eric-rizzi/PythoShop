#!/usr/bin/env python3
import argparse
import subprocess
import sys
import typing
import unittest
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def dummyInput(prompt=None):
    raise RuntimeError("You should not be calling the input function within your manipulation functions (only in __main__)")


def dummyRun(args, **kwargs):
    raise RuntimeError("You should not be calling the subprocess.run function within your manipulation functions (only in __main__)")


class SideBySideImage:
    _WIDTH = 200
    _SEPARATOR = 20
    _TEXT_VERTICAL_SPACE = 60

    def __init__(self, bytes: bytes, tag: str) -> None:
        full_image = Image.open(BytesIO(bytes))
        self.tag = tag

        self.width = SideBySideImage._WIDTH
        self.height = int(full_image.height * self.width / full_image.width)
        self.image = full_image.resize((self.width, self.height))

    @staticmethod
    def get_total_width(total_images: int) -> int:
        return total_images * SideBySideImage._WIDTH + (total_images + 1) * SideBySideImage._SEPARATOR

    @staticmethod
    def get_container_image(images: typing.List["SideBySideImage"]) -> Image.Image:
        total_width = SideBySideImage.get_total_width(len(images))
        max_height = max([image.height for image in images])

        return Image.new("RGB", (total_width, max_height + SideBySideImage._TEXT_VERTICAL_SPACE), "white")

    @staticmethod
    def add_title_to_container_image(
        combined_image: Image.Image,
        test_name: str,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.ImageFont,
    ) -> None:
        title = f"Failing Test: {test_name}, Time Stamp: {datetime.now().isoformat(timespec="seconds")}"
        text_x = combined_image.width // 2 - int(len(title) * 4)
        draw.text((text_x, 5), title, fill="red", font=font)

    def paste_into_image(
        self,
        combined_image: Image.Image,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.ImageFont,
        *,
        index: int,
    ) -> None:
        image_x = ((1 + index) * SideBySideImage._SEPARATOR) + (index * (SideBySideImage._WIDTH))
        combined_image.paste(self.image, (image_x, 30))

        text_x = (image_x + self.width // 2) - len(self.tag) * 5
        draw.text((text_x, combined_image.height - 25), self.tag, fill="black", font=font)


def _create_failure_visual(
    test_name: str,
    original_primary: bytes,
    original_secondary: typing.Optional[bytes],
    expected: bytes,
    failing_result: bytes,
) -> Image.Image:
    """
    Shows the expected and actual results after running a particular filter
    on an image.

    :param test_name: Name of test that failed
    :param original_primary: Primary image given to filter for processing
    :param original_secondary: Secondary image (maybe) given to filter
    :param expected: Expected result after running filter
    :param failing_result: Actual (failing) result after running filter
    :returns: Image containing all required pieces to explain failure
    """

    assert original_primary
    assert expected
    assert failing_result

    images = [SideBySideImage(original_primary, "Primary")]
    if original_secondary:
        images.append(SideBySideImage(original_secondary, "Secondary"))
    images.append(SideBySideImage(expected, "Expected"))
    images.append(SideBySideImage(failing_result, "Failing"))

    # Create a new blank image to hold the combined images
    combined_image = SideBySideImage.get_container_image(images)
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.load_default(size=16)
    SideBySideImage.add_title_to_container_image(combined_image, test_name, draw, font)

    # Paste the images side by side
    for index, image in enumerate(images):
        image.paste_into_image(combined_image, draw, font, index=index)

    return combined_image


class TestResult(unittest.TextTestResult):
    def __init__(self, stream: typing.TextIO, descriptions: bool, verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.separator1 = "\n" + self.separator1
        self.points_total = 0
        self.tests = []

    def addPoints(self, test) -> None:
        assert test.test_weight != 0, "Test " + str(test) + " has zero weight"
        assert type(test).__name__ == "Test" or type(test).__name__ == "Extension", "Test " + str(test) + ' is not named "Test" or "Extension"'
        if type(test).__name__ == "Test":
            self.points_total += test.test_weight

    def startTest(self, test) -> None:
        print(".", end="", flush=True)
        self.addPoints(test)
        self.tests.append(test)
        super().startTest(test)

    def addSkip(self, test, reason: str) -> None:
        super().addSkip(test, reason)
        # What a hack but I can't see any other way to get this
        skipped_module_name = test.description[test.description.find("(") + 1 : test.description.find(".")]
        skipped_class_name = test.description[test.description.find(".") + 1 : test.description.find(")")]
        print("#", end="", flush=True)
        if skipped_class_name == "Test":
            skipped_module = __import__(skipped_module_name)
            if skipped_class_name in dir(skipped_module):
                skipped_class = getattr(skipped_module, skipped_class_name)
                self.points_total += skipped_class.test_weight


def get_test_suite_results(*, pattern: typing.Optional[str] = None) -> TestResult:
    if pattern is None:
        pattern = "test*.py"
    else:
        pattern = f"test*{pattern}*py"

    testSuite = unittest.defaultTestLoader.discover("tests", pattern=pattern)
    testProgram = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    testProgram.resultclass = TestResult
    test_suite_results = testProgram.run(testSuite)
    return test_suite_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", help="Run all tests", default=False, required=False, action="store_true")
    args = parser.parse_args()

    # Disable parts of subprocess module so students don't get confused
    sys.modules["subprocess"].run = dummyRun

    if args.all:
        # Disable `input` so students don't get confused
        sys.modules["builtins"].input = dummyInput
        pattern_to_test = None
    else:
        pattern_to_test = input("Which filter/tool to test? ")
        while len(pattern_to_test) < 6 or not pattern_to_test.islower():
            print("Sorry, that doesn't look like a valid filter/tool")
            pattern_to_test = input("Which filter/tool to test? ")

    points_total = 0
    points_earned = 0
    tests_passed = []
    tests_partial = []
    tests_failed = []
    test_suite_results = get_test_suite_results(pattern=pattern_to_test)

    print("")
    print("Grade Breakdown")
    print("======================================================================")

    for test in test_suite_results.tests:
        print(f"Running test {test}")
        num_sub_tests = len(test.image_sets)
        sub_failures = [x for x in test_suite_results.failures if x[0].test_case == test]

        num_sub_failures = len(sub_failures)
        num_sub_success = num_sub_tests - num_sub_failures
        percentage = 0
        if num_sub_failures == 0:
            tests_passed.append(test.__module__)
            percentage = 1.0
        else:
            if num_sub_success > 0:
                tests_partial.append(test.__module__)
                # Get ~80% if passed at least one
                percentage = 0.75 + 0.25 * num_sub_success / num_sub_tests
            else:
                tests_failed.append(test.__module__)
                percentage = 0

            if pattern_to_test:
                failure_image = _create_failure_visual(
                    test_name=test.manip_func_name,
                    original_primary=test.original_primary_image,
                    original_secondary=test.original_secondary_image,
                    expected=test.expected_image,
                    failing_result=test.failing_image,
                )
                failure_image.show()

        percentage_str = str(round(percentage * 100))
        points = percentage * test.test_weight
        points_earned += points
        print(" " * (3 - len(percentage_str)) + percentage_str + "% " + str(test.__module__) + " (" + str(round(points, 1)) + " points)")

    points_total = int(1.15 * test_suite_results.points_total)
    for skip in test_suite_results.skipped:
        print("Skipped " + skip[1])

    print("")
    print("Grade Summary")
    print("======================================================================")
    if not pattern_to_test:
        print("  Total Points: " + str(points_total))

    print(" Points Earned: " + str(round(points_earned)))

    if not pattern_to_test:
        if points_total > 0:  # otherwise get a divide by zero
            print("Grade (approx): " + str(round(100 * points_earned / points_total)))
        else:
            print("Grade (approx): 0")
