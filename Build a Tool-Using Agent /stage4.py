# stage4.py
import json
import anthropic
client = anthropic.Anthropic()
tools = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event. Maximum 10 attendees.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string", "format": "email"}
                }
            },
            "required": ["title", "start", "end"]
        }
    }
]

def run_tool(name, tool_input):
    if name == "create_calendar_event":
        # Simulate a real-world limit: max 10 attendees
        if "attendees" in tool_input and len(tool_input["attendees"]) > 10:
            raise ValueError("Too many attendees — maximum is 10.")
        return {"event_id": "evt_123", "status": "created"}
    raise ValueError(f"Unknown tool: {name}")

# Ask Claude to invite 15 people — this will trigger the error
messages = [{
    "role": "user",
    "content": "Schedule an all-hands with: " + ", ".join(f"user{i}@work.com" for i in range(15))
}]
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

while response.stop_reason == "tool_use":
    tool_results = []

    for block in response.content:
        if block.type == "tool_use":
            try:
                result = run_tool(block.name, block.input)
                # Success
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })
            except Exception as e:
                # Failure — tell Claude what went wrong
                print(f" → Tool failed: {e}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(e),
                    "is_error": True # ← this flag tells Claude it went wrong
                })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    final = next(block for block in response.content if block.type == "text")
    print("\nFinal answer:", final.text)