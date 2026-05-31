# stage3.py
import json
import anthropic
client = anthropic.Anthropic()
tools = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"}
            },
            "required": ["title", "start", "end"]
        }
    },
    {
        "name": "list_calendar_events",
        "description": "List all events on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date"}
            },
            "required": ["date"]
        }
    }
]

def run_tool(name, tool_input):
 if name == "create_calendar_event":
    print(f" → Creating: {tool_input['title']}")
    return {"event_id": "evt_123", "status": "created"}
 if name == "list_calendar_events":
    print(f" → Listing events for: {tool_input['date']}")
    return {"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}
 return {"error": f"Unknown tool: {name}"}

messages = [{
    "role": "user",
    "content": "Check what I have next Monday, then schedule a planning session that avoids conflicts."
}]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

while response.stop_reason == "tool_use":
    # KEY CHANGE: collect ALL tool results before sending anything back
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"\n[Claude wants to call: {block.name}]")
            result = run_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result)
            })

    # Append Claude's full response and ALL results together
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