import sys

from test_runner import dummyRun, get_test_suite_results


def test_individual_function(name: str) -> None:
    test_suite_results = get_test_suite_results(pattern=name)

    test_results = list(test_suite_results.tests)
    if len(test_results) != 1:
        if len(test_results) == 0:
            print("Are you sure you have the right function name?")
            return
        else:
            print("Not specific enough")
            return

    for test in test_results:
        print(test)


if __name__ == "__main__":
    # Disable certain modules so students don't get confused
    sys.modules["subprocess"].run = dummyRun

    function_to_test = input("What function would you like to test? ").strip()
    test_individual_function(function_to_test)
