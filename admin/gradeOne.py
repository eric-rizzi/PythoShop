import importlib.util
import inspect
import subprocess
import sys

from tests.testRunner import assess_image_manip, dummyInput, dummyRun

STUDENT_FOLDER_TO_TEST = "/path/to/shared/folder"

if __name__ == "__main__":
    sys.modules["subprocess"].run = dummyRun
    sys.modules["builtins"].input = dummyInput

    print("Testing: " + STUDENT_FOLDER_TO_TEST)

    print("")
    print("Grade Breakdown")
    print("======================================================================")

    results = assess_image_manip(STUDENT_FOLDER_TO_TEST + "/PythoShop", verbosity=0)

    spec = importlib.util.spec_from_file_location("ImageManip", STUDENT_FOLDER_TO_TEST + "/PythoShop/ImageManip.py")
    manip_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manip_module)
    manip_function_names = [o[1].__name__ for o in inspect.getmembers(manip_module) if inspect.isfunction(o[1])]

    # Check for functions that aren't tested (in case students had misspellings)
    print("Functions not being tested:")
    for manip_function_name in manip_function_names:
        if manip_function_name not in results.functions_tested:
            if manip_function_name != "get_info" and not manip_function_name == "create_bmp":
                print("* " + manip_function_name)

    results.print_summary()
