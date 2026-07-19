from app.tools.filesystem_tools import (
    get_directory_tree,
    list_directory,
    read_file,
    search_files,
    get_file_info,
)

TOOL_REGISTRY = {
    "get_directory_tree": get_directory_tree,
    "list_directory": list_directory,
    "read_file": read_file,
    "search_files": search_files,
    "get_file_info": get_file_info,
}