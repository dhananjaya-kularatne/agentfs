from pathlib import Path
from app.config import settings


class PathValidationError(Exception):
    """Raised when a requested path escapes the sandbox working directory."""
    pass


def validate_path(relative_path: str) -> Path:
    """
    Resolve a user/agent-supplied relative path against the working directory,
    and ensure it does not escape the sandbox (blocks ../ traversal and symlink escapes).
    Returns the resolved, safe absolute Path.
    """
    working_dir = Path(settings.agent_working_directory).resolve()    # C:\agentfs\backend\sandbox
    candidate = (working_dir / relative_path).resolve()

    if not candidate.is_relative_to(working_dir):
        raise PathValidationError(
            f"Path '{relative_path}' resolves outside the working directory."
        )

    return candidate