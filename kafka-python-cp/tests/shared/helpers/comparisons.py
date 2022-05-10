from typing import Any

import numbers

PRINT_FORMAT = "{variable} ({type}): {value}"


def contains(actual: Any, expected: Any) -> bool:
    print(PRINT_FORMAT.format(variable="Actual", type=type(actual).__name__, value=repr(actual)))
    print(PRINT_FORMAT.format(variable="Expected", type=type(expected).__name__, value=repr(expected)))
    print()

    both_numbers = all(isinstance(value, numbers.Number) for value in (actual, expected))

    if not both_numbers and not isinstance(actual, type(expected)):
        return False

    if isinstance(expected, list):
        if not len(expected) == len(actual):
            print("List not of equal lenght")

            return False

        return all(contains(actual_value, expected_value) for (actual_value, expected_value) in zip(actual, expected))

    elif isinstance(expected, dict):
        return all(contains(actual.get(key, KeyError(key)), expected_value) for (key, expected_value) in expected.items())

    else:
        return expected == actual
