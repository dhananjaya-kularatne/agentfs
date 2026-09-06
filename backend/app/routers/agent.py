from fastapi import APIRouter, HTTPException, Header
from app.models.agent import AgentTaskRequest, AgentTaskResponse, ConfirmActionRequest
from app.services.agent_service import run_agent_task, resume_agent_task
from app.services.mongo_service import get_session, list_sessions, delete_session
from app.services.rate_limiter import task_rate_limiter

router = APIRouter()


def _enforce_rate_limit(client_id: str) -> None:
    """Reject the call with 429 if this client has exceeded its task budget."""
    if not task_rate_limiter.allow(client_id):
        raise HTTPException(
            status_code=429,
            detail="Too many agent requests. Slow down and try again shortly.",
            headers={"Retry-After": str(task_rate_limiter.retry_after(client_id))},
        )


@router.post("/api/agent/task", response_model=AgentTaskResponse)
async def create_agent_task(request: AgentTaskRequest, x_client_id: str = Header(...)):
    """Start a new agent task, scoped to the requesting client's own sandbox."""
    _enforce_rate_limit(x_client_id)
    result = await run_agent_task(request.goal, x_client_id)
    return AgentTaskResponse(**result)


@router.post("/api/agent/task/{session_id}/confirm", response_model=AgentTaskResponse)
async def confirm_agent_action(session_id: str, request: ConfirmActionRequest, x_client_id: str = Header(...)):
    """Approve or reject a pending destructive action, and resume the session."""
    _enforce_rate_limit(x_client_id)
    result = await resume_agent_task(session_id, request.approved, x_client_id)
    if result.get("status") == "failed" and result.get("error") in ("Session not found.", "Session is not awaiting confirmation."):
        raise HTTPException(status_code=404, detail=result["error"])
    return AgentTaskResponse(**result)


@router.get("/api/agent/sessions")
async def get_sessions(x_client_id: str = Header(...), limit: int = 50):
    """List sessions belonging only to the requesting client."""
    sessions = await list_sessions(x_client_id, limit)
    return {"sessions": sessions}


@router.get("/api/agent/sessions/{session_id}")
async def get_session_detail(session_id: str, x_client_id: str = Header(...)):
    """Fetch full detail for one session — only if it belongs to the requesting client."""
    session = await get_session(session_id)
    if session is None or session.get("client_id") != x_client_id:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.delete("/api/agent/sessions/{session_id}")
async def remove_session(session_id: str, x_client_id: str = Header(...)):
    """Delete a session — only if it belongs to the requesting client."""
    deleted = await delete_session(session_id, x_client_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}