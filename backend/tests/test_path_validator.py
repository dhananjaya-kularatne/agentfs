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