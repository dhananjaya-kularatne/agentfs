from app.tools.destructive_tools import delete_directory, write_file, move_file, delete_file
from app.tools.filesystem_tools import read_file


def test_write_file_creates_new_file(working_directory):
    result = write_file("temp_test_output.txt", "hello from a test", working_directory)
    assert result["success"] is True

    read_result = read_file("temp_test_output.txt", working_directory)
    assert read_result["data"] == "hello from a test"

    delete_file("temp_test_output.txt", working_directory)


def test_write_file_creates_parent_directories(working_directory):
    result = write_file("new_folder/nested_file.txt", "nested content", working_directory)
    assert result["success"] is True

    read_result = read_file("new_folder/nested_file.txt", working_directory)
    assert read_result["data"] == "nested content"

    delete_file("new_folder/nested_file.txt", working_directory)


def test_write_file_blocks_traversal(working_directory):
    result = write_file("../../evil.txt", "malicious content", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "path_validation"


def test_move_file_renames_successfully(working_directory):
    write_file("move_source.txt", "content to move", working_directory)
    result = move_file("move_source.txt", "move_dest.txt", working_directory)
    assert result["success"] is True

    read_result = read_file("move_dest.txt", working_directory)
    assert read_result["data"] == "content to move"

    delete_file("move_dest.txt", working_directory)


def test_move_file_refuses_existing_destination(working_directory):
    write_file("move_a.txt", "a", working_directory)
    write_file("move_b.txt", "b", working_directory)

    result = move_file("move_a.txt", "move_b.txt", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "destination_exists"

    delete_file("move_a.txt", working_directory)
    delete_file("move_b.txt", working_directory)


def test_delete_file_removes_file(working_directory):
    write_file("to_delete.txt", "temporary", working_directory)
    result = delete_file("to_delete.txt", working_directory)
    assert result["success"] is True

    read_result = read_file("to_delete.txt", working_directory)
    assert read_result["success"] is False
    assert read_result["error"]["type"] == "not_found"


def test_delete_file_refuses_directory(working_directory):
    result = delete_file("reports", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "is_a_directory"


def test_delete_file_nonexistent(working_directory):
    result = delete_file("does_not_exist.txt", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "not_found"


def test_delete_directory_removes_folder_and_contents(working_directory):
    write_file("temp_dir/inner.txt", "content", working_directory)
    result = delete_directory("temp_dir", working_directory)
    assert result["success"] is True
    assert result["data"]["files_removed"] == 1

    read_result = read_file("temp_dir/inner.txt", working_directory)
    assert read_result["success"] is False
    assert read_result["error"]["type"] == "not_found"


def test_delete_directory_counts_nested_contents(working_directory):
    write_file("count_test/a.txt", "a", working_directory)
    write_file("count_test/sub/b.txt", "b", working_directory)
    result = delete_directory("count_test", working_directory)
    assert result["success"] is True
    assert result["data"]["files_removed"] == 2
    assert result["data"]["folders_removed"] == 1


def test_delete_directory_refuses_file(working_directory):
    result = delete_directory("test.txt", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "not_a_directory"


def test_delete_directory_nonexistent(working_directory):
    result = delete_directory("does_not_exist_dir", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "not_found"


def test_delete_directory_blocks_traversal(working_directory):
    result = delete_directory("../../important_folder", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "path_validation"