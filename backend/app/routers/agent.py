from fastapi import APIRouter
from app.models.agent import AgentTaskRequest, AgentTaskResponse
from app.services.agent_service import run_agent_task

router = APIRouter()


@router.post("/api/agent/task", response_model=AgentTaskResponse)
def create_agent_task(request: AgentTaskRequest):
    """Run the agent loop against a natural-language goal."""
    result = run_agent_task(request.goal)
    return AgentTaskResponse(**result)