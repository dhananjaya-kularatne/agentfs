"""
Resource ceilings for filesystem tools.

The agent can be steered by task text or by the contents of files it reads, so
every tool that could be pushed into unbounded work needs a hard cap. These are
deliberately generous for the demo sandbox but small enough that a single call
cannot exhaust memory or wedge the process.
"""

# Largest file read_file will return, and largest payload write_file will accept.
MAX_FILE_BYTES = 1_048_576  # 1 MiB

# Most matches search_files will collect before it stops walking.
MAX_SEARCH_RESULTS = 1_000

# Hard ceiling on get_directory_tree depth and on the total nodes it will visit,
# regardless of what the caller asks for.
MAX_TREE_DEPTH = 8
MAX_TREE_NODES = 5_000
