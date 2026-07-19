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
]