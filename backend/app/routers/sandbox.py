from fastapi import APIRouter
from app.tools.filesystem_tools import get_directory_tree

router = APIRouter()


@router.get("/api/sandbox/tree")
def sandbox_tree():
    """Return the current sandbox directory tree, for display in the UI."""
    return get_directory_tree(".", max_depth=5)