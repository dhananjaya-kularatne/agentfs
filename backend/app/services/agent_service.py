import asyncio
import json
import uuid
from pathlib import Path
from groq import Groq
from app.config import settings
from app.tools.tool_definitions import TOOL_DEFINITIONS
from app.tools.tool_registry import TOOL_REGISTRY, DESTRUCTIVE_TOOLS
from app.tools.path_validator import validate_client_id, ClientIdValidationError
from app.services.mongo_service import create_session, get_session, update_session

_client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = (
    "You are a filesystem agent. You can explore, read, and modify files in a sandboxed "
    "working directory using the tools provided. Break the task into steps, use tools to gather "
    "the information you need, and give a final clear answer when you have enough information. "
    "Do not guess file contents you have not read.\n\n"
    "When the task calls for a destructive action (write_file, move_file, delete_file, "
    "delete_directory), CALL THE TOOL DIRECTLY. Do not ask the user for permission in your "
    "reply and do not stop to wait for approval: the system automatically intercepts every "
    "destructive tool call and asks the human to approve or reject it before it runs. Asking "
    "for confirmation in text instead of calling the tool leaves the task unfinished."
)

MAX_ITERATIONS = 10


def get_client_working_directory(client_id: str) -> Path:
    """
    Return the sandbox directory scoped to a specific client, creating and seeding it with baseline demo files on first use. This is the core of
    multi-user isolation: every client gets their own folder under the shared base sandbox path, so one visitor's files, uploads, and edits are never
    visible to another.

    The client ID is untrusted input from the ``X-Client-Id`` header. It is
    validated to a single safe path segment and the resolved directory is
    re-checked against the base, so a malicious value can never relocate the
    sandbox root outside ``agent_working_directory``. Raises
    ``ClientIdValidationError`` for a malformed ID.
    """
    validate_client_id(client_id)

    base = Path(settings.agent_working_directory).resolve()
    client_dir = (base / client_id).resolve()

    if not client_dir.is_relative_to(base) or client_dir == base:
        # Defence in depth: validate_client_id already rejects separators and
        # traversal, so reaching here means something upstream changed.
        raise ClientIdValidationError("Client ID does not resolve to a directory inside the sandbox.")

    if not client_dir.exists():
        client_dir.mkdir(parents=True, exist_ok=True)
        (client_dir / "test.txt").write_text("This is a test file for AgentFS.", encoding="utf-8")
        (client_dir / "meeting_notes.txt").write_text("Meeting notes from Monday.", encoding="utf-8")
        (client_dir / "reports").mkdir(exist_ok=True)
        (client_dir / "reports" / "q1_summary.txt").write_text("Q1 financial summary.", encoding="utf-8")

    return client_dir


async def run_agent_task(goal: str, client_id: str) -> dict:
    """Start a new agent session, scoped to this client's own sandbox directory."""
    session_id = str(uuid.uuid4())
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    await create_session(session_id, goal, client_id)
    working_directory = get_client_working_directory(client_id)
    return await _run_loop(session_id, messages, steps=[], seen_calls=set(), working_directory=working_directory)


async def resume_agent_task(session_id: str, approved: bool, client_id: str) -> dict:
    """Resume a paused session after a human approves or rejects the pending action."""
    session = await get_session(session_id)
    if session is None:
        return {"status": "failed", "error": "Session not found."}
    if session.get("client_id") != client_id:
        # Do not reveal whether the session exists under a different client — same error either way.
        return {"status": "failed", "error": "Session not found."}
    if session["status"] != "pending_confirm":
        return {"status": "failed", "error": "Session is not awaiting confirmation."}

    messages = session["messages"]
    steps = session["steps"]
    seen_calls = {tuple(c) for c in session.get("seen_calls", [])}
    pending = session["pending_action"]
    working_directory = get_client_working_directory(client_id)

    if approved:
        tool_function = TOOL_REGISTRY[pending["tool"]]
        result = tool_function(**pending["input"], working_directory=working_directory)
    else:
        result = {"success": False, "error": {"type": "rejected_by_user", "message": "The user rejected this action."}}

    steps.append({
        "type": "confirmation_result",
        "tool": pending["tool"],
        "input": pending["input"],
        "approved": approved,
        "output": result,
    })

    messages.append({
        "role": "tool",
        "tool_call_id": pending["tool_call_id"],
        "content": json.dumps(result),
    })

    return await _run_loop(session_id, messages, steps, seen_calls, working_directory)


async def _run_loop(session_id: str, messages: list, steps: list, seen_calls: set, working_directory: Path) -> dict:
    """Shared loop logic used by both starting and resuming a session."""
    for _ in range(MAX_ITERATIONS):
        try:
            # The Groq SDK call is blocking; run it off the event loop so one
            # in-flight task does not stall every other request on the server.
            response = await asyncio.to_thread(
                _client.chat.completions.create,
                model=settings.groq_model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
        except Exception as e:
            steps.append({"type": "llm_error", "message": str(e)})
            await update_session(session_id, {
                "status": "failed",
                "error": f"LLM generation failed: {str(e)}",
                "steps": steps,
                "total_steps": len(steps),
                "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
            })
            return {"status": "failed", "final_answer": None, "pending_action": None, "steps": steps, "error": f"LLM generation failed: {str(e)}", "session_id": session_id}

        message = response.choices[0].message

        # No tool calls means the model is done reasoning: this turn is the answer.
        if not message.tool_calls:
            steps.append({"type": "final_answer", "content": message.content})
            await update_session(session_id, {
                "status": "completed",
                "final_answer": message.content,
                "steps": steps,
                "messages": messages + [{"role": "assistant", "content": message.content}],
                "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
                "total_steps": len(steps),
            })
            return {"status": "completed", "final_answer": message.content, "pending_action": None, "steps": steps, "session_id": session_id, "error": None}

        # Replay the model's tool-calling turn into the history before executing the calls.
        assistant_message = {
            "role": "assistant",
            "content": message.content,
        }
        if message.tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        messages.append(assistant_message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Destructive tool: stop, persist a pending_confirm state, and wait for a human.
            if tool_name in DESTRUCTIVE_TOOLS:
                pending_action = {
                    "tool": tool_name,
                    "input": tool_args,
                    "tool_call_id": tool_call.id,
                }
                steps.append({"type": "confirmation_required", "tool": tool_name, "input": tool_args})
                await update_session(session_id, {
                    "status": "pending_confirm",
                    "pending_action": pending_action,
                    "steps": steps,
                    "messages": messages,
                    "seen_calls": list(seen_calls),
                    "total_steps": len(steps),
                    "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
                })
                return {"status": "pending_confirm", "final_answer": None, "pending_action": pending_action, "session_id": session_id, "steps": steps, "error": None}

            # Read-only tool: reject an exact repeat (stuck-loop guard), otherwise run it now.
            call_signature = (tool_name, json.dumps(tool_args, sort_keys=True))
            if call_signature in seen_calls:
                result = {"success": False, "error": {"type": "duplicate_call", "message": "You already called this exact tool with these exact arguments. Try a different approach."}}
            else:
                seen_calls.add(call_signature)
                tool_function = TOOL_REGISTRY.get(tool_name)
                result = tool_function(**tool_args, working_directory=working_directory) if tool_function else {"success": False, "error": {"type": "unknown_tool", "message": f"No such tool: {tool_name}"}}

            steps.append({"type": "tool_call", "tool": tool_name, "input": tool_args, "output": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

    # Loop exhausted without the model producing a final answer.
    await update_session(session_id, {
        "status": "failed",
        "error": "Max iterations reached.",
        "steps": steps,
        "total_steps": len(steps),
        "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
    })
    return {"status": "failed", "final_answer": None, "pending_action": None, "steps": steps, "error": "Max iterations reached.", "session_id": session_id}