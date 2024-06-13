#!/usr/bin/env python3
import os
import pickle
import random
import shutil
import typing
import unittest

import ImageManip
import tests.config as config
from tests.testBase import TestBase


def prep_expected_outputs_folder() -> None:
    """
    Cleans/creates the `expected_outputs` folder which is then filled with
    pickled and "expected" images for the tests.

    :returns: None
    """
    if os.path.exists(config.EXPECTED_OUTPUT_IMAGE_FOLDER):
        shutil.rmtree(config.EXPECTED_OUTPUT_IMAGE_FOLDER)

    os.mkdir(config.EXPECTED_OUTPUT_IMAGE_FOLDER)


def get_image_bytes_map() -> dict[str, bytes]:
    """
    Load all images used by test suite into a dictionary.

    :returns: Dict of image path -> bytes in image
    """
    image_to_bytes_map: dict[str, bytes] = {}
    for file_name in config.FILE_NAMES:
        file_name = file_name + ".bmp"
        file_path = os.path.join(config.IMAGES_FOLDER_PATH, file_name)

        with open(file_path, "rb") as fp:
            image_to_bytes_map[file_name] = fp.read()

    return image_to_bytes_map


def create_artifacts_for_tests(
    test_image_sets: list[list[str]],
    original_images: dict[str, bytes],
    *,
    test_base: TestBase,
) -> None:
    test_name = test_base.manip_func_name
    assert test_name

    print(f"Starting pickling of images for test {test_name}")
    solution_images: dict[str, bytes] = {}
    pickle_file_name = test_base.get_pickle_file_name()
    pickle_file_path = os.path.join(config.EXPECTED_OUTPUT_IMAGE_FOLDER, pickle_file_name)

    # Overall idea for test creation:
    # for each filter/tool
    #     for each image for testing filter/tool
    #         write original contents to test file
    #         run the transform on the file
    #         capture the output and write over the test file
    #     pickle all files created for filter/tool
    for original_file_names in test_image_sets:
        random.seed(0)  # make it predictably random
        original_files: list[typing.BinaryIO] = []

        solution_file_name = test_name + test_base.get_test_args_name() + "-" + "-".join(original_file_names) + ".bmp"
        solution_file_path = os.path.join(config.EXPECTED_OUTPUT_IMAGE_FOLDER, solution_file_name)

        solution_fp = open(solution_file_path, "wb+")
        solution_fp.write(original_images[original_file_names[0] + ".bmp"])
        original_files.append(solution_fp)
        solution_fp.seek(0)

        other_image = None
        if len(original_file_names) == 1:
            pass
        elif len(original_file_names) == 2:
            original_file_name = original_file_names[1] + ".bmp"
            other_image = open(os.path.join("images", original_file_name), "rb")
        else:
            raise (ValueError("Files for this test can be 1 or 2 files only"))

        testFunction = getattr(ImageManip, test_name)
        result = testFunction(*original_files, other_image=other_image, **test_base.test_parameters)
        if result is not None:
            solution_fp.close()
            solution_fp = open(solution_file_path, "wb+")
            result.seek(0)
            solution_fp.write(result.read())

        solution_fp.seek(0)
        solution_images[solution_file_name] = solution_fp.read()
        print(f"Pickling: {solution_file_name}")
        solution_fp.close()

    print(f"Outputting pickled images into {pickle_file_path}")
    pickled_solution_images = open(pickle_file_path, "wb")
    pickle.dump(solution_images, pickled_solution_images)
    pickled_solution_images.close()


if __name__ == "__main__":
    # Pickle up the original images as inputs for tests

    print("Starting pickling of original images.")
    prep_expected_outputs_folder()
    original_images = get_image_bytes_map()

    with open(config.TEST_ORIGINALS_PICKLE_FILE_NAME, "wb") as pickle_fp:
        pickle.dump(original_images, pickle_fp)
    print(f"Outputting pickled images into {config.TEST_ORIGINALS_PICKLE_FILE_NAME}")

    # Pickle the expected output for each test/transformation
    print('Starting creating and pickling of "expected output" images')

    testSuite = unittest.defaultTestLoader.discover(".")
    for test in testSuite:
        if test.countTestCases() == 0:
            continue

        print(f"Creating artifacts for test {test}")
        test_base = test._tests[0]._tests[0]

        test_image_sets = test_base.image_sets
        if test_image_sets is None:
            # Unless otherwise specified, use all images
            test_image_sets = list([file_name] for file_name in config.FILE_NAMES)

        create_artifacts_for_tests(
            test_image_sets,
            original_images,
            test_base=test_base,
        )
