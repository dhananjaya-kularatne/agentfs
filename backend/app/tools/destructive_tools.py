import shutil
from app.tools.path_validator import validate_path, PathValidationError


def write_file(path: str, content: str) -> dict:
    """Create or overwrite a file with the given content."""
    try:
        target = validate_path(path)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as e:
        return {"success": False, "error": {"type": "write_failed", "message": str(e)}}

    return {"success": True, "data": {"path": path, "bytes_written": len(content.encode("utf-8"))}}


def move_file(src: str, dest: str) -> dict:
    """Move or rename a file/folder."""
    try:
        src_target = validate_path(src)
        dest_target = validate_path(dest)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not src_target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"'{src}' does not exist."}}
    if dest_target.exists():
        return {"success": False, "error": {"type": "destination_exists", "message": f"'{dest}' already exists."}}

    try:
        dest_target.parent.mkdir(parents=True, exist_ok=True)
        src_target.rename(dest_target)
    except OSError as e:
        return {"success": False, "error": {"type": "move_failed", "message": str(e)}}

    return {"success": True, "data": {"from": src, "to": dest}}


def delete_file(path: str) -> dict:
    """Delete a file."""
    try:
        target = validate_path(path)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"'{path}' does not exist."}}
    if target.is_dir():
        return {"success": False, "error": {"type": "is_a_directory", "message": f"'{path}' is a directory. This tool only deletes files."}}

    try:
        target.unlink()
    except OSError as e:
        return {"success": False, "error": {"type": "delete_failed", "message": str(e)}}

    return {"success": True, "data": {"deleted": path}}

def delete_directory(path: str) -> dict:
    """Permanently delete a directory and everything inside it."""
    try:
        target = validate_path(path)
    except PathValidationError as e:
        return {"success": False, "error": {"type": "path_validation", "message": str(e)}}

    if not target.exists():
        return {"success": False, "error": {"type": "not_found", "message": f"'{path}' does not exist."}}
    if not target.is_dir():
        return {"success": False, "error": {"type": "not_a_directory", "message": f"'{path}' is a file. Use delete_file instead."}}

    all_items = list(target.rglob("*"))
    file_count = sum(1 for i in all_items if i.is_file())
    folder_count = sum(1 for i in all_items if i.is_dir())

    try:
        shutil.rmtree(target)
    except OSError as e:
        return {"success": False, "error": {"type": "delete_failed", "message": str(e)}}

    return {
        "success": True,
        "data": {"deleted": path, "files_removed": file_count, "folders_removed": folder_count},
    }