import json
from groq import Groq
from app.config import settings
from app.tools.tool_definitions import TOOL_DEFINITIONS
from app.tools.tool_registry import TOOL_REGISTRY

_client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = (
    "You are a filesystem agent. You can explore and read files in a sandboxed "
    "working directory using the tools provided. Break the task into steps, "
    "use tools to gather the information you need, and give a final clear answer "
    "when you have enough information. Do not guess file contents you have not read."
)

MAX_ITERATIONS = 10


def run_agent_task(goal: str) -> dict:
    """
    Run the observe -> reason -> act loop until the agent produces a final answer,
    hits the iteration cap, or gets stuck repeating the same tool call.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    steps = []
    seen_calls = set()

    for iteration in range(MAX_ITERATIONS):
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:
            steps.append({"type": "final_answer", "content": message.content})
            return {"status": "completed", "final_answer": message.content, "steps": steps}

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            call_signature = (tool_name, json.dumps(tool_args, sort_keys=True))
            if call_signature in seen_calls:
                steps.append({
                    "type": "stuck_warning",
                    "tool": tool_name,
                    "input": tool_args,
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({
                        "success": False,
                        "error": {
                            "type": "duplicate_call",
                            "message": "You already called this exact tool with these exact arguments. Try a different approach."
                        }
                    }),
                })
                continue

            seen_calls.add(call_signature)

            tool_function = TOOL_REGISTRY.get(tool_name)
            if tool_function is None:
                result = {"success": False, "error": {"type": "unknown_tool", "message": f"No such tool: {tool_name}"}}
            else:
                result = tool_function(**tool_args)

            steps.append({
                "type": "tool_call",
                "tool": tool_name,
                "input": tool_args,
                "output": result,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

    return {"status": "failed", "final_answer": None, "steps": steps, "error": "Max iterations reached."}