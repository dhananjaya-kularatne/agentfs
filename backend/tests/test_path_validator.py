import pytest
from app.tools.path_validator import validate_path, PathValidationError


def test_valid_path_inside_sandbox():
    """A normal relative path inside the sandbox should resolve successfully."""
    result = validate_path("test.txt")
    assert result.name == "test.txt"


def test_valid_nested_path():
    """A path inside a subfolder should also resolve successfully."""
    result = validate_path("reports/q1_summary.txt")
    assert result.name == "q1_summary.txt"


def test_blocks_parent_directory_traversal():
    """A path attempting to escape via ../ should raise PathValidationError."""
    with pytest.raises(PathValidationError):
        validate_path("../../Windows/System32")


def test_blocks_absolute_path_outside_sandbox():
    """An absolute path pointing outside the sandbox should raise PathValidationError."""
    with pytest.raises(PathValidationError):
        validate_path("C:/Windows/System32")


def test_blocks_deeply_nested_traversal():
    """Multiple levels of ../ chained together should still be caught."""
    with pytest.raises(PathValidationError):
        validate_path("reports/../../../../etc/passwd")

def test_url_encoded_sequences_treated_as_literal_filename():
    """
    URL-encoded traversal sequences are not decoded by this function -
    they're treated as literal (harmless) filenames, since paths reach this
    function as plain strings, not raw URL-encoded HTTP segments.
    """
    result = validate_path("%2e%2e")
    assert result.name == "%2e%2e"


def test_blocks_null_byte_in_path():
    """A null byte in the path should not bypass validation."""
    with pytest.raises((PathValidationError, ValueError)):
        validate_path("test.txt\x00.jpg")


def test_empty_path_resolves_to_working_directory():
    """An empty path should resolve to the working directory itself, not error."""
    result = validate_path("")
    assert result.exists()


def test_blocks_traversal_via_current_directory_tricks():
    """Mixed ./ and ../ sequences should still be caught."""
    with pytest.raises(PathValidationError):
        validate_path("./reports/../../../../../etc/passwd")