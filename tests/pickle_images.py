#!/usr/bin/env python3
import os
import pickle
import random
import unittest

import tests.test_files as test_files

# import image_manip_solution

IMAGES_FOLDER_PATH = "tests/images"
PICKLE_FILE_NAME = "test_originals.pickle"


if __name__ == "__main__":
    # Pickle up the original images as inputs for tests
    original_images: dict[str, bytes] = {}

    for file_name in test_files.FILE_NAMES:
        file_name = file_name + ".bmp"
        file_path = os.path.join(IMAGES_FOLDER_PATH, file_name)

        with open(file_path, "rb") as fp:
            original_images[file_name] = fp.read()
            print("Pickling: " + file_name + " in " + PICKLE_FILE_NAME)

    with open(PICKLE_FILE_NAME, "wb") as pickle_fp:
        pickle.dump(original_images, pickle_fp)

    # Pickle the expected output for each test/transformation
    testSuite = unittest.defaultTestLoader.discover(".")
    for test in testSuite:
        if test.countTestCases() == 0:
            continue

        test_name = test._tests[0]._tests[0].manip_func_name
        test_args = test._tests[0]._tests[0].test_parameters
        test_image_sets = test._tests[0]._tests[0].image_sets
        args_name = ""
        for param, value in test_args.items():
            args_name += "_" + param + "_" + str(value)

        solution_images: dict[str, bytes] = {}
        pickle_file_name = test._tests[0]._tests[0].__module__ + ".pickle"
        if test_image_sets is None:
            test_image_sets = list([file_name] for file_name in test_files.FILE_NAMES)

        for original_file_names in test_image_sets:
            random.seed(0)  # make it predictably random
            original_files = []
            solution_file_name = test_name + args_name + "-" + "-".join(original_file_names) + ".bmp"
            solution_file = open(solution_file_name, "wb+")
            solution_file.write(original_images[original_file_names[0] + ".bmp"])
            original_files.append(solution_file)
            solution_file.seek(0)
            for original_file_name in original_file_names[1:]:
                original_file_name = original_file_name + ".bmp"
                original_file = open(original_file_name, "rb")
                original_files.append(original_file)
            testFunction = getattr(image_manip_solution, test_name)
            result = testFunction(*original_files, **test_args)
            if result is not None:
                solution_file.close()
                solution_file = open(solution_file_name, "wb+")
                result.seek(0)
                solution_file.write(result.read())
            solution_file.seek(0)
            solution_images[solution_file_name] = solution_file.read()
            print("Pickling: " + solution_file_name + " in " + pickle_file_name)
            solution_file.close()

        pickled_solution_images = open(pickle_file_name, "wb")
        pickle.dump(solution_images, pickled_solution_images)
        pickled_solution_images.close()
