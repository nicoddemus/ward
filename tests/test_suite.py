from types import ModuleType
from unittest import mock

from python_tester.fixtures import Fixture, FixtureRegistry, fixture
from python_tester.suite import Suite
from python_tester.test import Test
from python_tester.test_result import TestResult

NUMBER_OF_TESTS = 5


@fixture
def module():
    return ModuleType("test_module")


@fixture
def fixtures():
    return {
        "fixture_a": Fixture(key="fixture_a", fn=lambda fixture_b: fixture_b * 2),
        "fixture_b": Fixture(key="fixture_b", fn=lambda: 2),
    }


@fixture
def example_test(module, fixtures):
    return Test(fn=lambda fixture_a: fixture_a, module=module)


@fixture
def fixture_registry(fixtures):
    registry = FixtureRegistry()
    registry._fixtures = fixtures
    return registry


@fixture
def suite(example_test, fixture_registry):
    return Suite(tests=[example_test] * NUMBER_OF_TESTS, fixture_registry=fixture_registry)


def test_suite_num_tests(suite):
    assert suite.num_tests == NUMBER_OF_TESTS


def test_suite_num_fixtures(suite, fixtures):
    assert suite.num_fixtures == len(fixtures)


def test_generate_test_runs__correct_number_of_runs_generated(suite):
    runs = suite.generate_test_runs()
    assert len(list(runs)) == NUMBER_OF_TESTS


def test_generate_test_runs__yields_correct_test_results_when_exhausted(suite):
    results = list(suite.generate_test_runs())
    assert results == [
        TestResult(test=test, was_success=True, error=None, message="") for test in suite.tests
    ]


def test_generate_test_runs__yields_failing_test_result_on_failed_assertion(
    fixture_registry, module
):
    def test_i_fail():
        assert False

    test = Test(fn=test_i_fail, module=module)
    failing_suite = Suite(tests=[test], fixture_registry=fixture_registry)

    results = failing_suite.generate_test_runs()
    result = next(results)

    assert result == TestResult(test=test, was_success=False, error=mock.ANY, message="")
    assert type(result.error) is AssertionError