from pydantic import BaseModel


class AgentTaskRequest(BaseModel):
    """A natural-language task for the agent to perform."""
    goal: str


class AgentTaskResponse(BaseModel):
    """Result of running an agent task."""
    status: str
    session_id: str | None = None
    final_answer: str | None
    steps: list[dict]
    pending_action: dict | None = None
    error: str | None = None


class ConfirmActionRequest(BaseModel):
    """A human's decision on a pending destructive action."""
    approved: bool