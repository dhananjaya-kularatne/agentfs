from pydantic import BaseModel


class AgentTaskRequest(BaseModel):
    """A natural-language task for the agent to perform."""
    goal: str


class AgentTaskResponse(BaseModel):
    """Result of running an agent task."""
    status: str
    final_answer: str | None
    steps: list[dict]
    error: str | None = None