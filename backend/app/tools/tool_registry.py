from app.tools.filesystem_tools import (
    get_directory_tree,
    list_directory,
    read_file,
    search_files,
    get_file_info,
)
from app.tools.destructive_tools import write_file, move_file, delete_file

TOOL_REGISTRY = {
    "get_directory_tree": get_directory_tree,
    "list_directory": list_directory,
    "read_file": read_file,
    "search_files": search_files,
    "get_file_info": get_file_info,
    "write_file": write_file,
    "move_file": move_file,
    "delete_file": delete_file,
}

DESTRUCTIVE_TOOLS = {"write_file", "move_file", "delete_file"}