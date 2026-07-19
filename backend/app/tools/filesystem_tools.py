from pathlib import Path
from app.tools.path_validator import validate_path, PathValidationError


def get_directory_tree(path: str = ".", max_depth: int = 3) -> dict:
    """Return a nested folder/file structure starting at path, up to max_depth."""
    try:
        target = validate_path(path)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    #Checks whether the file exist
    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"Path '{path}' does not exist."}}

    def build_tree(current: Path, depth: int) -> dict:
        node = {"name": current.name, "type": "directory" if current.is_dir() else "file"}
        if current.is_dir() and depth < max_depth:
            node["children"] = [
                build_tree(child, depth + 1) for child in sorted(current.iterdir())
            ]
        return node

    return {"success": True, "data": build_tree(target, 0)}


def list_directory(path: str = ".") -> dict:
    """List immediate files and folders inside path (non-recursive)."""
    try:
        target = validate_path(path)
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


def read_file(path: str) -> dict:
    """Read and return the text contents of a file."""
    try:
        target = validate_path(path)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"File '{path}' does not exist."}}
    if target.is_dir():
        return {"success": False, "error": {"type": "is_a_directory", "message": f"'{path}' is a directory, not a file."}}

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"success": False, "error": {"type": "binary_file", "message": f"'{path}' is a binary file and cannot be read as text."}}

    return {"success": True, "data": content}


def search_files(pattern: str, path: str = ".") -> dict:
    """Find files matching a glob pattern (e.g. '*.txt') within path, recursively."""
    try:
        target = validate_path(path)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists() or not target.is_dir():
        return {"success": False, "error": {"type": "not_found", "message": f"Directory '{path}' does not exist."}}

    matches = [str(p.relative_to(target)) for p in target.rglob(pattern)]
    return {"success": True, "data": matches}


def get_file_info(path: str) -> dict:
    """Return size, type, and last-modified date for a file or folder."""
    try:
        target = validate_path(path)
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