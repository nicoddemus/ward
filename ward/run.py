import argparse
import sys
from typing import Any, Dict

from blessings import Terminal

from ward.collect import get_info_for_modules, get_tests_in_modules, load_modules
from ward.fixtures import fixture_registry
from ward.suite import Suite
from ward.terminal import TestResultWriter


def setup_cmd_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path of directory containing tests")
    return parser


def run():
    term = Terminal()

    cmd_line = setup_cmd_line()
    args: Dict[str, Any] = vars(cmd_line.parse_args())

    path_to_tests = args.get("path", ".") or "."
    mod_infos = get_info_for_modules(path_to_tests)
    modules = list(load_modules(mod_infos))
    tests = list(get_tests_in_modules(modules))

    suite = Suite(tests=tests, fixture_registry=fixture_registry)

    test_results = suite.generate_test_runs()

    exit_code = TestResultWriter(
        suite=suite,
        terminal=term,
        test_results=test_results,
    ).write_test_results_to_terminal()

    sys.exit(exit_code.value)


if __name__ == "__main__":
    run()