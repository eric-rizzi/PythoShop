import ast
import importlib
import os
import typing
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


class SideBySideImage:
    _WIDTH = 200
    _SEPARATOR = 20
    _TEXT_VERTICAL_SPACE = 60

    def __init__(
        self,
        bytes: bytes,
        tag: str,
    ) -> None:
        self.orig_image = Image.open(BytesIO(bytes))
        self.tag = tag

        self.width = SideBySideImage._WIDTH
        self.height = int(self.orig_image.height * self.width / self.orig_image.width)
        self.image = self.orig_image.resize((self.width, self.height))

    def resize(self, rel_max_width: int) -> None:
        self.width = int((self.orig_image.width / rel_max_width) * SideBySideImage._WIDTH)
        self.height = int(self.orig_image.height * self.width / self.orig_image.width)
        self.image = self.orig_image.resize((self.width, self.height))

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
        title = f"Function: {test_name}, Time Stamp: {datetime.now().isoformat()}"
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
    alters_size: bool,
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

    if alters_size:
        max_width = max([i.orig_image.width for i in images])
        for i in images:
            i.resize(max_width)

    # Create a new blank image to hold the combined images
    combined_image = SideBySideImage.get_container_image(images)
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.load_default()
    SideBySideImage.add_title_to_container_image(combined_image, test_name, draw, font)

    # Paste the images side by side
    for index, image in enumerate(images):
        image.paste_into_image(combined_image, draw, font, index=index)

    return combined_image


def get_image_bytes(file_name: str) -> BytesIO:
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


class FilterInfo:
    def __init__(
        self,
        is_required: bool,
        points: typing.Optional[int] = None,
        image: str = "daisies.bmp",
        secondary_image: typing.Optional[str] = None,
        color: tuple[int, int, int] = (255, 100, 20),
        extra: str = "45,66,71",
        alters_size: bool = False,
    ):
        if is_required:
            assert points == None
        else:
            assert points is not None

        self.is_required = is_required
        self.points = points
        self.image = image
        self.secondary_image = secondary_image
        self.color = color
        self.extra = extra
        self.alters_size = alters_size


class CheckResult(typing.NamedTuple):
    exists: bool
    passed: typing.Optional[bool] = None
    message: typing.Optional[str] = None
    percentage_correct: typing.Optional[float] = None


POINTS = {
    # Change Pixel
    "change_pixel": FilterInfo(is_required=True, image="blank.bmp"),
    "mark_middle": FilterInfo(is_required=True, image="blank.bmp"),
    "say_hi": FilterInfo(is_required=False, points=10, image="uchicago.bmp"),
    # Change Multiple Pixels
    "mark_four_corners": FilterInfo(is_required=True, image="blank.bmp"),
    "mark_middle_with_t": FilterInfo(is_required=True, image="blank.bmp"),
    "draw_t": FilterInfo(is_required=True, image="blank.bmp"),
    "draw_rainbow": FilterInfo(is_required=False, points=10, image="blank.bmp"),
    # # Drawing Lines
    "draw_hline": FilterInfo(is_required=True, image="blank.bmp"),
    "draw_vline": FilterInfo(is_required=True, image="blank.bmp"),
    "draw_centered_hline": FilterInfo(is_required=False, points=5),
    "draw_centered_vline": FilterInfo(is_required=False, points=5),
    "draw_sloping_lines": FilterInfo(is_required=False, points=5),
    "draw_frame": FilterInfo(is_required=False, points=5),
    # Pixel Parts
    "make_red": FilterInfo(is_required=True),
    "make_static": FilterInfo(is_required=True),
    "remove_red": FilterInfo(is_required=True),
    "remove_green": FilterInfo(is_required=True),
    "remove_blue": FilterInfo(is_required=True),
    "max_red": FilterInfo(is_required=False, points=2),
    "max_green": FilterInfo(is_required=False, points=2),
    "max_blue": FilterInfo(is_required=False, points=2),
    "only_red": FilterInfo(is_required=False, points=2),
    "only_blue": FilterInfo(is_required=False, points=2),
    "only_green": FilterInfo(is_required=False, points=2),
    # Value Based Changes
    "lighten": FilterInfo(is_required=True),
    "make_gray": FilterInfo(is_required=True),
    "negate": FilterInfo(is_required=True),
    "darken": FilterInfo(is_required=False, points=5),
    "negate_red": FilterInfo(is_required=False, points=2),
    "negate_blue": FilterInfo(is_required=False, points=2),
    "negate_green": FilterInfo(is_required=False, points=2),
    "swap_grb": FilterInfo(is_required=False, points=3),
    "swap_bgr": FilterInfo(is_required=False, points=3),
    "redify": FilterInfo(is_required=False, points=7),
    "greenify": FilterInfo(is_required=False, points=7),
    "magentify": FilterInfo(is_required=False, points=7),
    # Conditional
    "intensify": FilterInfo(is_required=True),
    "make_two_tone": FilterInfo(is_required=True, color=(255, 255, 255), extra="0,0,0"),
    "make_four_tone": FilterInfo(is_required=True, color=(255, 255, 255), extra="0, 0, 0", image="bear.bmp"),
    "make_custom_two_tone": FilterInfo(is_required=False, points=10),
    "make_n_tone": FilterInfo(is_required=False, points=20, extra="3", color=(255, 255, 255), image="bear.bmp"),
    "saturate": FilterInfo(is_required=False, points=30),
    # Blending
    "make_better_two_tone": FilterInfo(is_required=True, color=(255, 255, 255), extra="0, 0, 0"),
    "blend_other": FilterInfo(is_required=True, image="underwater.bmp", secondary_image="scuba.bmp"),
    "chroma_overlay": FilterInfo(is_required=True, image="underwater.bmp", secondary_image="scuba.bmp", color=(0, 255, 0)),
    "blend_other_diff_sizes": FilterInfo(is_required=False, image="underwater.bmp", secondary_image="dog.bmp", points=5),
    "blend_other_percentages": FilterInfo(is_required=False, image="underwater.bmp", secondary_image="scuba.bmp", points=5, extra=".2"),
    "better_chroma_overlay": FilterInfo(is_required=False, image="underwater.bmp", secondary_image="bear.bmp", points=10, color=(193, 193, 202)),
    "chroma_overlay_stamp": FilterInfo(is_required=False, image="underwater.bmp", secondary_image="scuba.bmp", points=15, color=(0, 255, 0)),
    # Pixel Positions
    # "make_line_drawing": FilterInfo(is_required=True, color=(0, 0, 0)),
    # "mirror_left_horizontal": FilterInfo(is_required=True, image="scuba.bmp"),
    # "shrink": FilterInfo(is_required=True, alters_size=True),
    # "fade_in_vertical": FilterInfo(is_required=True, color=(0, 0, 0)),
    # "fade_in_horizontal": FilterInfo(is_required=False, points=3, color=(0, 0, 0)),
    # "fade_out_horizontal": FilterInfo(is_required=False, points=3, color=(0, 0, 0)),
    # "fade_color_in_vertical": FilterInfo(is_required=False, points=8),
    # "blend_gradual_horizontal": FilterInfo(is_required=False, image="underwater.bmp", secondary_image="scuba.bmp", points=10),
    # "mirror_right_horizontal": FilterInfo(is_required=False, points=5),
    # "mirror_top_vertical": FilterInfo(is_required=False, points=5),
    # "enlarge": FilterInfo(is_required=False, alters_size=True, points=10),
    # "better_shrink": FilterInfo(is_required=False, alters_size=True, points=15),
    # "better_enlarge": FilterInfo(is_required=False, alters_size=True, points=15),
}


def get_percentage_correct(function_name: str) -> float:
    while True:
        try:
            result_str = input(f"Testing {function_name}. How similar do they look (0-10)? ").strip()
            if len(result_str) > 2 or (len(result_str) == 2 and result_str[0] == "0"):
                continue
            result = int(result_str)
            if 0 <= result <= 10:
                return result / 10
            elif result > 10:
                return 1.0
        except ValueError:
            continue


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
    ret = get_image_bytes(image_path)
    ret.seek(0)
    return ret


def execute_function(
    function: typing.Callable,
    image_name: str,
    filter_info: FilterInfo,
    image_secondary_name: typing.Optional[str] = None,
) -> bytes:
    image_bytes_io_primary = load_image(image_name)
    if image_secondary_name:
        image_bytes_io_secondary = load_image(image_secondary_name)
    else:
        image_bytes_io_secondary = None

    try:
        kwargs = {"color": filter_info.color, "other_image": image_bytes_io_secondary, "extra": filter_info.extra}
        result = function(image_bytes_io_primary, **kwargs)
    except TypeError:
        # Filter
        kwargs = {"clicked_coordinate": (20, 20), "color": filter_info.color, "other_image": image_bytes_io_secondary, "extra": filter_info.extra}
        result = function(image_bytes_io_primary, **kwargs)

    if not result:
        result = image_bytes_io_primary
    result.seek(0)
    return result.read()


def check_single_function(function_name) -> CheckResult:
    print(f"Checking {function_name}")
    filter_info = POINTS.get(function_name)
    if not filter_info:
        return CheckResult(exists=False, message="There is no function by that name.")

    fn = load_function("image_manip", function_name)
    if not fn:
        return CheckResult(exists=False, message=f"Missing {function_name} in your `image_manip.py` file")

    with open(os.path.join("tests", "expected_outputs", f"{function_name}.bmp"), "rb") as fp:
        expected_bytes = fp.read()

    image_name = filter_info.image
    image_secondary_name = filter_info.secondary_image
    try:
        actual_bytes = execute_function(fn, image_name, filter_info, image_secondary_name)

        orig_bytes = load_image(image_name).read()
        if image_secondary_name:
            secondary_bytes = load_image(image_secondary_name).read()
        else:
            secondary_bytes = None

        failure_image = _create_failure_visual(
            test_name=function_name,
            original_primary=orig_bytes,
            original_secondary=secondary_bytes,
            expected=expected_bytes,
            failing_result=actual_bytes,
            alters_size=filter_info.alters_size,
        )
        failure_image.show()
        result = get_percentage_correct(function_name)
        return CheckResult(exists=True, passed=bool(result > 0.99), percentage_correct=result)
    except (TypeError, ValueError, ZeroDivisionError, NameError) as e:
        return CheckResult(exists=True, passed=False, message=str(e))

    except AttributeError:
        # Likely didn't convert a string to an int
        return CheckResult(exists=True, passed=False, message="Failed with AttributeError error")

    except OverflowError:
        # Something is wrong with their function
        return CheckResult(exists=True, passed=False, message="Failed with OverFlow error")


def check_all_functions_exist() -> None:
    existing_functions = get_decorated_function_names("image_manip.py")
    if not existing_functions:
        print("No decorated (e.g., @export_filter, @export_tool) functions found")
        return

    required = {k for k, v in POINTS.items() if v.is_required}
    print(f"The following required functions are missing: {required.difference(existing_functions)}")
    print(f"You might have some misspelled functions: {existing_functions.difference(POINTS.keys())}")


def check_all_functions() -> None:
    existing_functions = get_decorated_function_names("image_manip.py")
    if not existing_functions:
        print("No decorated (e.g., @export_filter, @export_tool) functions found")
        return

    required_functions_missing = []
    required_functions_failing = []
    extensions_failing = []

    required_possible_points = 0
    required_actual_points = 0
    extension_points = 0

    for function_name, function_info in POINTS.items():
        result = check_single_function(function_name)
        if result.exists:
            if function_name in existing_functions:
                existing_functions.remove(function_name)

        if function_info.is_required:
            required_possible_points += 1
            required_actual_points += 1.0 * result.percentage_correct if result.percentage_correct else 0

            if not result.exists:
                required_functions_missing.append(function_name)
            elif not result.passed:
                required_functions_failing.append(function_name)

        else:
            if result.exists:
                extension_points += function_info.points * result.percentage_correct if result.percentage_correct else 0
                if not result.passed:
                    extensions_failing.append(function_name)

    print(f"The following required functions are missing: {required_functions_missing}")
    print(f"The following required functions are failing: {required_functions_failing}")
    print(f"The following extension functions are failing: {extensions_failing}")
    print(f"You have {extension_points} points in extensions")
    if existing_functions:
        print(f"You might have some misspelled functions: {existing_functions}")

    base_score = (required_actual_points / required_possible_points) * 87
    extension_score = (extension_points / 120) * 13
    print(f"Total predicted grade is {base_score + extension_score}")


if __name__ == "__main__":
    ans = input('What filter/tool would you like to test (type "all" for all)? ').strip().lower()
    if ans == "all":
        check_all_functions_exist()
        check_all_functions()
    else:
        result = check_single_function(ans)
        if not result.exists:
            if result.message:
                print(result.message)
            else:
                print("There is no function by that name. Are you sure you spelled it right?")
        elif result.passed:
            filter_info = POINTS[ans]
            if filter_info.is_required:
                print("Great job! Another required function down!")
            else:
                print(f"Great job! That's {filter_info.points} points in extensions")

        elif result.message:
            print(f"There was an issue. The function didn't run because it {result.message}")
        else:
            print("Keep trying!")
