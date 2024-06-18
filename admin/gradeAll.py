import csv
import glob
import importlib.util
import io
import os
import subprocess
import sys
import unittest

import students

from tests.testRunner import assess_image_manip, dummyInput, dummyRun

if __name__ == "__main__":
    sys.modules["subprocess"].run = dummyRun
    sys.modules["builtins"].input = dummyInput

    test_files = []
    for i in range(0, 7):
        test_files += glob.glob(f"tests/test_{i}*.py")
    test_files.sort()

    with open("./results.csv", "w") as results_fp:
        columns = ["Name", "Total"]
        for test_file in test_files:
            test_package = test_file[: test_file.find(".")]
            test_name = test_package.split("/")[-1]
            columns.append(test_name)

        writer = csv.DictWriter(results_fp, fieldnames=columns)
        writer.writeheader()

        for student_folder in students.STUDENT_FOLDERS:
            print("Testing: " + student_folder)
            student_name = student_folder.split("/")[-1]
            os.environ["PYTEST_TIMEOUT"] = "2"

            results = assess_image_manip(student_folder + "/PythoShop", verbosity=2)

            writer.writerow(results.get_csv_row(student_name))
