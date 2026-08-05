import pytest
from app.tools.path_validator import validate_path, PathValidationError


def test_valid_path_inside_sandbox(working_directory):
    result = validate_path("test.txt", working_directory)
    assert result.name == "test.txt"


def test_valid_nested_path(working_directory):
    result = validate_path("reports/q1_summary.txt", working_directory)
    assert result.name == "q1_summary.txt"


def test_blocks_parent_directory_traversal(working_directory):
    with pytest.raises(PathValidationError):
        validate_path("../../Windows/System32", working_directory)


def test_blocks_absolute_path_outside_sandbox(working_directory):
    with pytest.raises(PathValidationError):
        validate_path("C:/Windows/System32", working_directory)


def test_blocks_deeply_nested_traversal(working_directory):
    with pytest.raises(PathValidationError):
        validate_path("reports/../../../../etc/passwd", working_directory)


def test_url_encoded_sequences_treated_as_literal_filename(working_directory):
    result = validate_path("%2e%2e", working_directory)
    assert result.name == "%2e%2e"


def test_blocks_null_byte_in_path(working_directory):
    with pytest.raises((PathValidationError, ValueError)):
        validate_path("test.txt\x00.jpg", working_directory)


def test_empty_path_resolves_to_working_directory(working_directory):
    result = validate_path("", working_directory)
    assert result.exists()


def test_blocks_traversal_via_current_directory_tricks(working_directory):
    with pytest.raises(PathValidationError):
        validate_path("./reports/../../../../../etc/passwd", working_directory)