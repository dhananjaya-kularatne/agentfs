from fastapi import APIRouter, HTTPException
from app.models.agent import AgentTaskRequest, AgentTaskResponse, ConfirmActionRequest
from app.services.agent_service import resume_agent_task, run_agent_task

router = APIRouter()


@router.post("/api/agent/task", response_model=AgentTaskResponse)
async def create_agent_task(request: AgentTaskRequest):
    """Start a new agent task."""
    result = await run_agent_task(request.goal)
    return AgentTaskResponse(**result)


@router.post("/api/agent/task/{session_id}/confirm", response_model=AgentTaskResponse)
async def confirm_agent_action(session_id: str, request: ConfirmActionRequest):
    """Approve or reject a pending destructive action, and resume the session."""
    result = await resume_agent_task(session_id, request.approved)
    if result.get("status") == "failed" and result.get("error") in ("Session not found.", "Session is not awaiting confirmation."):
        raise HTTPException(status_code=404, detail=result["error"])
    return AgentTaskResponse(**result)