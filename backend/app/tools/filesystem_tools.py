from pathlib import Path
from app.tools.path_validator import validate_path, PathValidationError
from app.tools.limits import (
    MAX_FILE_BYTES,
    MAX_SEARCH_RESULTS,
    MAX_TREE_DEPTH,
    MAX_TREE_NODES,
)


def get_directory_tree(path: str, working_directory: Path, max_depth: int = 3) -> dict:
    """Return a nested folder/file structure starting at path, up to max_depth."""
    try:
        target = validate_path(path, working_directory)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"Path '{path}' does not exist."}}

    # Clamp the requested depth so a large or malicious value cannot drive an
    # unbounded walk, and stop entirely once the node budget is spent.
    effective_depth = max(0, min(max_depth, MAX_TREE_DEPTH))
    node_count = 0
    truncated = False

    def build_tree(current: Path, depth: int) -> dict:
        nonlocal node_count, truncated
        node = {"name": current.name, "type": "directory" if current.is_dir() else "file"}
        if current.is_dir() and depth < effective_depth:
            children = []
            for child in sorted(current.iterdir()):
                if node_count >= MAX_TREE_NODES:
                    truncated = True
                    break
                node_count += 1
                children.append(build_tree(child, depth + 1))
            node["children"] = children
        return node

    tree = build_tree(target, 0)
    result = {"success": True, "data": tree}
    if truncated:
        result["truncated"] = True
    return result


def list_directory(path: str, working_directory: Path) -> dict:
    """List immediate files and folders inside path (non-recursive)."""
    try:
        target = validate_path(path, working_directory)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"Path '{path}' does not exist."}}
    if not target.is_dir():
        return {"success": False, "error": {"type": "not_a_directory", "message": f"'{path}' is not a directory."}}

    items = [
        {"name": item.name, "type": "directory" if item.is_dir() else "file"}
        for item in sorted(target.iterdir())
    ]
    return {"success": True, "data": items}


def read_file(path: str, working_directory: Path) -> dict:
    """Read and return the text contents of a file."""
    try:
        target = validate_path(path, working_directory)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"File '{path}' does not exist."}}
    if target.is_dir():
        return {"success": False, "error": {"type": "is_a_directory", "message": f"'{path}' is a directory, not a file."}}

    if target.stat().st_size > MAX_FILE_BYTES:
        return {"success": False, "error": {"type": "file_too_large", "message": f"'{path}' exceeds the {MAX_FILE_BYTES}-byte read limit."}}

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"success": False, "error": {"type": "binary_file", "message": f"'{path}' is a binary file and cannot be read as text."}}

    return {"success": True, "data": content}


def search_files(pattern: str, path: str, working_directory: Path) -> dict:
    """Find files matching a glob pattern (e.g. '*.txt') within path, recursively."""
    try:
        target = validate_path(path, working_directory)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists() or not target.is_dir():
        return {"success": False, "error": {"type": "not_found", "message": f"Directory '{path}' does not exist."}}

    matches = []
    truncated = False
    for p in target.rglob(pattern):
        if len(matches) >= MAX_SEARCH_RESULTS:
            truncated = True
            break
        matches.append(str(p.relative_to(target)))

    result = {"success": True, "data": matches}
    if truncated:
        result["truncated"] = True
    return result


def get_file_info(path: str, working_directory: Path) -> dict:
    """Return size, type, and last-modified date for a file or folder."""
    try:
        target = validate_path(path, working_directory)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"Path '{path}' does not exist."}}

    stat = target.stat()
    return {
        "success": True,
        "data": {
            "name": target.name,
            "type": "directory" if target.is_dir() else "file",
            "size_bytes": stat.st_size,
            "modified": stat.st_mtime,
        }
    }