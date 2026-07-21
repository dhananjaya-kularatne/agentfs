TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_directory_tree",
            "description": "Get the nested folder/file structure starting at a path, up to a max depth. Use this first to understand the overall layout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to start from. Use '.' for the root."},
                    "max_depth": {"type": "integer", "description": "How many levels deep to traverse. Default 3."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the immediate files and folders inside a path (not recursive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to list. Use '.' for the root."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the text contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file to read."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Find files matching a glob pattern (e.g. '*.txt', 'report*') recursively within a path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern to match filenames against."},
                    "path": {"type": "string", "description": "Directory to search within. Use '.' for the root."}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_info",
            "description": "Get size, type, and last-modified date for a file or folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file or folder."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a new file or overwrite an existing file with the given text content. This is a destructive action and requires human confirmation before it takes effect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path where the file should be written."},
                    "content": {"type": "string", "description": "The text content to write into the file."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_file",
            "description": "Move or rename a file. Fails if the destination already exists. This is a destructive action and requires human confirmation before it takes effect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "src": {"type": "string", "description": "Relative path to the file to move."},
                    "dest": {"type": "string", "description": "Relative destination path."}
                },
                "required": ["src", "dest"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Permanently delete a file. Cannot delete directories. This is a destructive action and requires human confirmation before it takes effect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file to delete."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_directory",
            "description": "Permanently delete a directory and everything inside it, including all files and subfolders. This is a destructive action and requires human confirmation before it takes effect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the directory to delete."}
                },
                "required": ["path"]
            }
        }
    },
]