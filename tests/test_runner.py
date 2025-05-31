import ast
import importlib
import os
import sys
import typing
import unittest
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


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
        title = f"Function: {test_name}, Time Stamp: {datetime.now().isoformat(timespec="seconds")}"
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
    images.append(SideBySideImage(failing_result, "Actual"))

    # Create a new blank image to hold the combined images
    combined_image = SideBySideImage.get_container_image(images)
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.load_default(size=16)
    SideBySideImage.add_title_to_container_image(combined_image, test_name, draw, font)

    # Paste the images side by side
    for index, image in enumerate(images):
        image.paste_into_image(combined_image, draw, font, index=index)

    return combined_image


def dummyInput(prompt=None):
    raise RuntimeError("You should not be calling the input function within your manipulation functions (only in __main__)")


def dummyRun(
    args,
    *,
    stdin=None,
    input=None,
    stdout=None,
    stderr=None,
    capture_output=False,
    shell=False,
    cwd=None,
    timeout=None,
    check=False,
    encoding=None,
    errors=None,
    text=None,
    env=None,
    universal_newlines=None,
):
    raise RuntimeError("You should not be calling the subprocess.run function within your manipulation functions (only in __main__)")


class TestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.separator1 = "\n" + self.separator1
        self.points_total = 0
        self.tests = []

    def addPoints(self, test):
        assert test.test_weight != 0, "Test " + str(test) + " has zero weight"
        assert type(test).__name__ == "Test" or type(test).__name__ == "Extension", "Test " + str(test) + ' is not named "Test" or "Extension"'
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


def _get_image_bytes(file_name: str) -> BytesIO:
    if os.path.splitext(file_name)[-1].lower() == ".bmp":
        # Load it directly rather than going through Pillow where we might loose some fidelity (e.g. paddding bytes)
        current_bytes = BytesIO()
        current_bytes.write(open(file_name, "rb").read())
    else:
        current_bytes = BytesIO()
        img = Image.open(file_name)
        img = img.convert("RGB")
        img.save(current_bytes, format="bmp")
        img.close()

    return current_bytes


def load_function(module_name, function_name_str) -> typing.Optional[typing.Callable]:
    """
    Dynamically loads a function from a module and executes it.

    Args:
        module_name (str): The name of the module to import (e.g., "image_manip").
        function_name_str (str): The name of the function to load.
        *args: Positional arguments to pass to the loaded function.
        **kwargs: Keyword arguments to pass to the loaded function.

    Returns:
        The result of the function call, or None if an error occurs.
    """
    try:
        # Import the module
        module = importlib.import_module(module_name)

        # Get the function from the module
        try:
            return getattr(module, function_name_str)
        except AttributeError:
            return None

    except ModuleNotFoundError:
        print(f"Error: Module '{module_name}.py' not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


class FilterInfo(typing.NamedTuple):
    is_required: bool
    requires_secondary: bool
    points: int
    image: str = "daisies.bmp"


class CheckResult(typing.NamedTuple):
    exists: bool
    passed: typing.Optional[bool] = None
    message: typing.Optional[str] = None


POINTS = {
    # Change Pixel
    "change_pixel": FilterInfo(is_required=True, requires_secondary=False, points=10, image="blank.bmp"),
    "mark_middle": FilterInfo(is_required=True, requires_secondary=False, points=10, image="blank.bmp"),
    "say_hi": FilterInfo(is_required=False, requires_secondary=False, points=10, image="uchicago.bmp"),
    #
    "lighten": FilterInfo(is_required=True, requires_secondary=False, points=10),
    "make_gray": FilterInfo(is_required=True, requires_secondary=False, points=10),
    "negate": FilterInfo(is_required=True, requires_secondary=False, points=10),
    "darken": FilterInfo(is_required=False, requires_secondary=False, points=5),
    "negate_red": FilterInfo(is_required=False, requires_secondary=False, points=2),
    "negate_blue": FilterInfo(is_required=False, requires_secondary=False, points=2),
    "negate_green": FilterInfo(is_required=False, requires_secondary=False, points=2),
    "swap_grb": FilterInfo(is_required=False, requires_secondary=False, points=3),
    "swap_bgr": FilterInfo(is_required=False, requires_secondary=False, points=3),
    "redify": FilterInfo(is_required=False, requires_secondary=False, points=7),
    "greenify": FilterInfo(is_required=False, requires_secondary=False, points=7),
    "magentify": FilterInfo(is_required=False, requires_secondary=False, points=7),
}


def get_decorated_function_names(file_path: str) -> set[str]:
    """
    Parses a Python file and returns a list of function and method names
    that are decorated with any of the TARGET_DECORATOR_NAMES.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list: A list of strings, where each string is the name of a
              function or method decorated with one of the target decorators.
              Returns an empty list if the file doesn't exist, can't be read,
              or contains syntax errors.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return set()

    found_function_names = set()
    try:
        with open(file_path, "r", encoding="utf-8") as source_file:
            source_code = source_file.read()

        # Parse the source code into an Abstract Syntax Tree
        tree = ast.parse(source_code, filename=file_path)

        # Traverse the AST to find functions and class methods
        for node in ast.walk(tree):
            # Check for functions (ast.FunctionDef) or async functions (ast.AsyncFunctionDef)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.decorator_list:
                    for decorator in node.decorator_list:
                        decorator_name = None
                        if isinstance(decorator, ast.Name):  # Decorator like @my_decorator
                            decorator_name = decorator.id
                        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                            # Decorator like @my_decorator(arg1, arg2)
                            # decorator.func gives the Name object for the decorator itself
                            decorator_name = decorator.func.id

                        if decorator_name and decorator_name in ["export_tool", "export_filter"]:
                            found_function_names.add(node.name)
                            break  # Found a target decorator, no need to check others for this function

    except SyntaxError as e:
        print(f"Error: Could not parse '{file_path}' due to a syntax error: {e}")
        return set()
    except Exception as e:
        print(f"An unexpected error occurred while processing '{file_path}': {e}")
        return set()

    return found_function_names


def load_image(image_name: str) -> BytesIO:
    image_path = os.path.join(os.path.dirname(__file__), f"../images/{image_name}")
    ret = _get_image_bytes(image_path)
    ret.seek(0)
    return ret


def execute_function(function: typing.Callable, image_name: str, image_secondary_name: typing.Optional[str] = None) -> bytes:
    image_bytes_io_primary = load_image(image_name)
    if image_secondary_name:
        image_bytes_io_secondary = load_image(image_secondary_name)
    else:
        image_bytes_io_secondary = None

    result = function(image_bytes_io_primary, clicked_coordinate=(20, 20), color=(255, 100, 20), other_image=image_bytes_io_secondary, extra="45,66,71")
    if not result:
        result = image_bytes_io_primary
    result.seek(0)
    return result.read()


def check_single_function(function_name) -> CheckResult:
    filter_info = POINTS.get(function_name)
    if not filter_info:
        return CheckResult(exists=False, message="No function by that name")

    r1 = load_function("tests.obfuscated_manip", function_name)
    assert r1

    r2 = load_function("image_manip", function_name)
    if not r2:
        return CheckResult(exists=False, message=f"Missing {function_name}")

    image_path = filter_info.image
    expected_bytes = execute_function(r1, image_path)
    actual_bytes = execute_function(r2, image_path)

    orig_bytes = load_image(image_path).read()
    if filter_info.requires_secondary:
        secondary_bytes = load_image(image_path).read()
    else:
        secondary_bytes = None

    failure_image = _create_failure_visual(
        test_name=function_name,
        original_primary=orig_bytes,
        original_secondary=secondary_bytes,
        expected=expected_bytes,
        failing_result=actual_bytes,
    )
    failure_image.show()
    same = input(f"Testing {function_name}. Do they look the same? ").strip().lower()
    if same.startswith("y"):
        return CheckResult(exists=True, passed=True)
    else:
        return CheckResult(exists=True, passed=False)


def check_all_functions() -> None:
    existing_functions = get_decorated_function_names("image_manip.py")
    if not existing_functions:
        return

    required_functions_missing = set()
    required_functions_failing = set()

    extension_points = 0

    for function_name, function_info in POINTS.items():
        result = check_single_function(function_name)
        if result.exists:
            existing_functions.remove(function_name)

        if function_info.is_required:
            if not result.exists:
                required_functions_missing.add(function_name)
            elif not result.passed:
                required_functions_failing.add(function_name)

        else:
            if result.passed:
                extension_points += function_info.points

    print(f"The following required functions are missing: {required_functions_missing}")
    print(f"The following required functions are failing: {required_functions_failing}")
    print(f"You have {extension_points} points in extensions")
    if existing_functions:
        print(f"You might have some misspelled functions: {existing_functions}")


if __name__ == "__main__":
    ans = input('What filter/tool would you like to test (type "all" for all)? ').strip().lower()
    if ans == "all":
        check_all_functions()
    else:
        result = check_single_function(ans)
        if not result.exists:
            print("There is no function by that name. Are you sure you spelled it right?")
        elif result.passed:
            print("Great job!")
        else:
            print("Keep trying!")
