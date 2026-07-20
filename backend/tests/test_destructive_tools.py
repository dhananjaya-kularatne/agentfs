from app.tools.destructive_tools import write_file, move_file, delete_file
from app.tools.filesystem_tools import read_file


def test_write_file_creates_new_file():
    result = write_file("temp_test_output.txt", "hello from a test")
    assert result["success"] is True

    read_result = read_file("temp_test_output.txt")
    assert read_result["data"] == "hello from a test"

    delete_file("temp_test_output.txt")


def test_write_file_creates_parent_directories():
    result = write_file("new_folder/nested_file.txt", "nested content")
    assert result["success"] is True

    read_result = read_file("new_folder/nested_file.txt")
    assert read_result["data"] == "nested content"

    delete_file("new_folder/nested_file.txt")


def test_write_file_blocks_traversal():
    result = write_file("../../evil.txt", "malicious content")
    assert result["success"] is False
    assert result["error"]["type"] == "path_validation"


def test_move_file_renames_successfully():
    write_file("move_source.txt", "content to move")
    result = move_file("move_source.txt", "move_dest.txt")
    assert result["success"] is True

    read_result = read_file("move_dest.txt")
    assert read_result["data"] == "content to move"

    delete_file("move_dest.txt")


def test_move_file_refuses_existing_destination():
    write_file("move_a.txt", "a")
    write_file("move_b.txt", "b")

    result = move_file("move_a.txt", "move_b.txt")
    assert result["success"] is False
    assert result["error"]["type"] == "destination_exists"

    delete_file("move_a.txt")
    delete_file("move_b.txt")


def test_delete_file_removes_file():
    write_file("to_delete.txt", "temporary")
    result = delete_file("to_delete.txt")
    assert result["success"] is True

    read_result = read_file("to_delete.txt")
    assert read_result["success"] is False
    assert read_result["error"]["type"] == "not_found"


def test_delete_file_refuses_directory():
    result = delete_file("reports")
    assert result["success"] is False
    assert result["error"]["type"] == "is_a_directory"


def test_delete_file_nonexistent():
    result = delete_file("does_not_exist.txt")
    assert result["success"] is False
    assert result["error"]["type"] == "not_found"