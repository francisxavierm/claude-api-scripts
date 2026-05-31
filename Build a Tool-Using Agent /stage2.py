# stage2.py
import json
import anthropic
client = anthropic.Anthropic()
tools = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event with attendees.",
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

# This is the actual function that "does the work".
def run_tool(name, tool_input):
 if name == "create_calendar_event":
    print(f" → Creating event: {tool_input['title']}")
    return {"event_id": "evt_123", "status": "created", "title": tool_input["title"]}
 return {"error": f"Unknown tool: {name}"}

# Keep a running history of all messages so Claude never loses context.
messages = [{
    "role": "user",
    "content": "Schedule a weekly team standup every Monday at 9am for 4 weeks. Invite alice@work.com, bob@work.com, carol@work.com."
}]

# First API call
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

# THE LOOP — keep going while Claude wants to call tools
while response.stop_reason == "tool_use":
    tool_results = []

    for block in response.content:
        if block.type == "tool_use":
            result = run_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result)
            })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

 # Call Claude again with the updated history
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

 # Loop ended — Claude is done
final = next(block for block in response.content if block.type == "text")
print("\nFinal answer:", final.text)