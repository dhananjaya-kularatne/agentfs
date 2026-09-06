import re
from pathlib import Path

class PathValidationError(Exception):
    """Raised when a requested path escapes the sandbox working directory."""
    pass


class ClientIdValidationError(Exception):
    """Raised when a client identifier is malformed or unsafe to use as a path segment."""
    pass


# A client ID is used directly as a directory name under the shared sandbox root,
# so it must be a single, boring path segment with no separators or traversal.
# crypto.randomUUID() on the frontend produces 36 chars of [0-9a-f-]; allow a
# little more room for alternative schemes without opening the door to abuse.
_CLIENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,128}$")


def validate_client_id(client_id: str) -> str:
    """
    Validate an untrusted client identifier before it is ever joined to a
    filesystem path. The client ID arrives in the ``X-Client-Id`` header and is
    used to build each browser's private sandbox root, so an unchecked value
    (``../..``, an absolute path, a null byte) would relocate the sandbox root
    itself and defeat every downstream path check. Returns the ID unchanged when
    it is safe; raises ``ClientIdValidationError`` otherwise.
    """
    if not isinstance(client_id, str):
        raise ClientIdValidationError("Client ID must be a string.")
    if "\x00" in client_id:
        raise ClientIdValidationError("Client ID contains a null byte, which is not allowed.")
    if not _CLIENT_ID_PATTERN.fullmatch(client_id):
        raise ClientIdValidationError(
            "Client ID must be 8-128 characters of letters, digits, hyphen, or underscore."
        )
    return client_id


def validate_path(relative_path: str, working_directory: Path) -> Path:
    """
    Resolve a user/agent-supplied relative path against the working directory,
    and ensure it does not escape the sandbox (blocks ../ traversal and symlink escapes).
    Returns the resolved, safe absolute Path.
    """

    if "\x00" in relative_path:
        raise PathValidationError("Path contains a null byte, which is not allowed.")

    working_dir = working_directory.resolve()    # C:\agentfs\backend\sandbox
    candidate = (working_dir / relative_path).resolve()

    if not candidate.is_relative_to(working_dir):
        raise PathValidationError(
            f"Path '{relative_path}' resolves outside the working directory."
        )

    return candidate
