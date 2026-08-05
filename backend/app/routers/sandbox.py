from fastapi import APIRouter, Header
from app.tools.filesystem_tools import get_directory_tree
from app.services.agent_service import get_client_working_directory

router = APIRouter()


@router.get("/api/sandbox/tree")
def sandbox_tree(x_client_id: str = Header(...)):
    """Return the requesting client's own sandbox directory tree, for display in the UI."""
    working_directory = get_client_working_directory(x_client_id)
    return get_directory_tree(".", working_directory, max_depth=5)