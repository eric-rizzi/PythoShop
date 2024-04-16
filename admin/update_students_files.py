#!/usr/bin/env python3
import glob
import os
import shutil
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWGRP, S_IWOTH, S_IWRITE

import students

PYTHOSHOP_FILE_PATHS_TO_COPY = [
    "__init__.py",
    "pythoshop.kv",
    "pythoshop.py",
    "pythoshop_exports.py",
    "pythoshop.code-workspace",
]
VSCODE_FILE_PATHS_TO_COPY = [
    ".vscode-students/launch.json",
]


def copy_readonly_files(files: list[str], destination_folder: str) -> None:
    # print("Verifying folder exists...")
    try:
        os.makedirs(destination_folder)
    except FileExistsError:
        pass

    # print("Copying to " + destination_folder)
    for file in files:
        # print("    Copying " + str(file))
        destination_file = os.path.join(destination_folder, os.path.basename(file))
        try:
            os.chmod(destination_file, S_IWRITE | S_IWGRP | S_IWOTH)
        except:
            pass
        shutil.copy(file, destination_file)
        os.chmod(destination_file, S_IREAD | S_IRGRP | S_IROTH)


def get_base_test_files() -> list[str]:
    base_test_files = []
    base_test_files += glob.glob("tests/config.py")
    base_test_files += glob.glob("tests/test_base*")
    base_test_files += glob.glob("tests/test_run*")
    base_test_files += glob.glob("tests/test_tool*")
    base_test_files += glob.glob("tests/config.py")
    base_test_files += glob.glob("images/change*")
    base_test_files += glob.glob("tests/test_0*")

    return base_test_files


TEST_FILES: dict[int, list[str]] = {}
TEST_FILES[0] = get_base_test_files()
TEST_FILES[1] = glob.glob("tests/test_1*")
TEST_FILES[2] = glob.glob("tests/test_2*")
TEST_FILES[3] = glob.glob("tests/test_3*")
TEST_FILES[4] = glob.glob("tests/test_4*")
TEST_FILES[5] = glob.glob("tests/test_5*")
TEST_FILES[6] = glob.glob("tests/test_6*")


if __name__ == "__main__":

    ASSIGNMENT_NUMBER = 1
    test_files_to_copy = []
    for i in range(0, ASSIGNMENT_NUMBER + 1):
        test_files_to_copy += TEST_FILES[i]

    for student_folder in students.STUDENT_FOLDERS:
        student_folder = os.path.join(student_folder, "PythoShop")
        copy_readonly_files(PYTHOSHOP_FILE_PATHS_TO_COPY, student_folder)

        student_vscode_folder = os.path.join(student_folder, ".vscode")
        copy_readonly_files(VSCODE_FILE_PATHS_TO_COPY, student_vscode_folder)

        student_test_folder = os.path.join(student_folder, "tests")
        copy_readonly_files(test_files_to_copy, student_test_folder)

        image_manip = os.path.join(student_folder, "image_manip.py")
        if not os.path.exists(image_manip):
            shutil.copy("image_manip_blank.py", image_manip)
