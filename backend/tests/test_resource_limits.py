from app.tools.filesystem_tools import read_file, search_files, get_directory_tree
from app.tools.destructive_tools import write_file
from app.tools.limits import MAX_FILE_BYTES, MAX_SEARCH_RESULTS, MAX_TREE_DEPTH


def test_read_file_rejects_oversized_file(working_directory):
    big = working_directory / "big.bin"
    big.write_bytes(b"a" * (MAX_FILE_BYTES + 1))

    result = read_file("big.bin", working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "file_too_large"


def test_read_file_allows_file_at_the_limit(working_directory):
    ok = working_directory / "ok.txt"
    ok.write_bytes(b"a" * MAX_FILE_BYTES)

    result = read_file("ok.txt", working_directory)
    assert result["success"] is True


def test_write_file_rejects_oversized_content(working_directory):
    result = write_file("huge.txt", "x" * (MAX_FILE_BYTES + 1), working_directory)
    assert result["success"] is False
    assert result["error"]["type"] == "content_too_large"


def test_search_files_caps_results(working_directory):
    bulk = working_directory / "bulk"
    bulk.mkdir()
    for i in range(MAX_SEARCH_RESULTS + 50):
        (bulk / f"f{i}.log").write_text("x", encoding="utf-8")

    result = search_files("*.log", "bulk", working_directory)
    assert result["success"] is True
    assert len(result["data"]) == MAX_SEARCH_RESULTS
    assert result.get("truncated") is True


def test_directory_tree_clamps_excessive_depth(working_directory):
    # Build a chain deeper than the hard ceiling.
    current = working_directory
    for i in range(MAX_TREE_DEPTH + 5):
        current = current / f"lvl{i}"
        current.mkdir()

    result = get_directory_tree(".", working_directory, max_depth=9999)
    assert result["success"] is True

    depth = 0
    node = result["data"]
    while node.get("children"):
        match = [c for c in node["children"] if c["name"].startswith("lvl")]
        if not match:
            break
        node = match[0]
        depth += 1
    assert depth <= MAX_TREE_DEPTH
