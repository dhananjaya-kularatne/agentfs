from app.tools.filesystem_tools import (
    get_directory_tree,
    list_directory,
    read_file,
    search_files,
    get_file_info,
)


def test_list_directory_returns_expected_items():
    result = list_directory(".")
    assert result["success"] is True
    names = [item["name"] for item in result["data"]]
    assert "test.txt" in names
    assert "reports" in names


def test_list_directory_nonexistent_path():
    result = list_directory("does_not_exist")
    assert result["success"] is False
    assert result["error"]["type"] == "not_found"


def test_read_file_returns_content():
    result = read_file("test.txt")
    assert result["success"] is True
    assert "test file" in result["data"].lower()


def test_read_file_on_directory_fails_cleanly():
    result = read_file("reports")
    assert result["success"] is False
    assert result["error"]["type"] == "is_a_directory"


def test_read_file_nonexistent_fails_cleanly():
    result = read_file("ghost.txt")
    assert result["success"] is False
    assert result["error"]["type"] == "not_found"


def test_search_files_finds_txt_files():
    result = search_files("*.txt")
    assert result["success"] is True
    assert any("test.txt" in match for match in result["data"])
    assert any("q1_summary.txt" in match for match in result["data"])


def test_get_file_info_returns_size_and_type():
    result = get_file_info("test.txt")
    assert result["success"] is True
    assert result["data"]["type"] == "file"
    assert result["data"]["size_bytes"] > 0


def test_get_directory_tree_includes_nested_folder():
    result = get_directory_tree(".")
    assert result["success"] is True
    child_names = [child["name"] for child in result["data"]["children"]]
    assert "reports" in child_names


def test_path_validation_blocks_traversal_in_tools():
    """Confirm tools reject traversal attempts, not just the raw validator."""
    result = read_file("../../../etc/passwd")
    assert result["success"] is False
    assert result["error"]["type"] == "path_validation"