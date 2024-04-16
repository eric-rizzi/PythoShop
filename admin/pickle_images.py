#!/usr/bin/env python3
import os
import pickle
import random
import unittest

import image_manip
import tests.test_files as test_files

IMAGES_FOLDER_PATH = "images"
EXPECTED_OUTPUT_IMAGE_FOLDER = "images/expected_outputs"
PICKLE_FILE_NAME = "images/test_originals.pickle"


if __name__ == "__main__":
    # Pickle up the original images as inputs for tests
    original_images: dict[str, bytes] = {}

    print("Starting pickling of original images.")
    for file_name in test_files.FILE_NAMES:
        file_name = file_name + ".bmp"
        file_path = os.path.join(IMAGES_FOLDER_PATH, file_name)

        with open(file_path, "rb") as fp:
            original_images[file_name] = fp.read()
            print(f"Pickling: {file_name}")

    with open(PICKLE_FILE_NAME, "wb") as pickle_fp:
        pickle.dump(original_images, pickle_fp)
    print(f"Outputting pickled images into {PICKLE_FILE_NAME}")

    # Pickle the expected output for each test/transformation
    print('Starting creating and pickling of "expected output" images')
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
        pickle_file_path = os.path.join(EXPECTED_OUTPUT_IMAGE_FOLDER, pickle_file_name)

        print(f"Starting pickling of images for test {test_name}")
        if test_image_sets is None:
            # Unless otherwise specified, use all images
            test_image_sets = list([file_name] for file_name in test_files.FILE_NAMES)

        for original_file_names in test_image_sets:
            random.seed(0)  # make it predictably random
            original_files = []

            solution_file_name = test_name + args_name + "-" + "-".join(original_file_names) + ".bmp"
            solution_file_path = os.path.join(EXPECTED_OUTPUT_IMAGE_FOLDER, solution_file_name)

            # Something about:
            # 1. Write origin contents to test file
            # 2. Run the transform on the file
            # 3. Capture the output and write over the test file
            solution_file = open(solution_file_path, "wb+")
            solution_file.write(original_images[original_file_names[0] + ".bmp"])
            original_files.append(solution_file)
            solution_file.seek(0)
            for original_file_name in original_file_names[1:]:
                original_file_name = original_file_name + ".bmp"
                original_file = open(original_file_name, "rb")
                original_files.append(original_file)
            testFunction = getattr(image_manip, test_name)
            result = testFunction(*original_files, **test_args)
            if result is not None:
                solution_file.close()
                solution_file = open(solution_file_path, "wb+")
                result.seek(0)
                solution_file.write(result.read())

            solution_file.seek(0)
            solution_images[solution_file_name] = solution_file.read()
            print(f"Pickling: {solution_file_name}")
            solution_file.close()

        print(f"Outputting pickled images into {pickle_file_path}")
        pickled_solution_images = open(pickle_file_path, "wb")
        pickle.dump(solution_images, pickled_solution_images)
        pickled_solution_images.close()
