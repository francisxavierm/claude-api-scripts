# stage5.py
import json
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

# Use @beta_tool to turn a normal Python function into a tool.
# The SDK reads the type hints and docstring to build the JSON schema for you.

@beta_tool
def create_calendar_event(
    title: str,
    start: str,
    end: str,
    attendees: list[str] | None = None
) -> str:
    """Create a calendar event.

    Args:
        title: Event title.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        attendees: Email addresses to invite.
    """
 
    if attendees and len(attendees) > 10:
        raise ValueError("Too many attendees — max 10.")
    return json.dumps({"event_id": "evt_123", "status": "created", "title": title})

@beta_tool
def list_calendar_events(date: str) -> str:
    """List all calendar events on a given date.
    Args:
    date: Date in YYYY-MM-DD format.
    """
    return json.dumps({
    "events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]
    })

# tool_runner replaces the while loop entirely.
# .until_done() runs until stop_reason is "end_turn".
final_message = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[create_calendar_event, list_calendar_events],
    messages=[{
        "role": "user",
        "content": "Check what I have next Monday, then schedule a planning session that avoids conflicts."
    }]
).until_done()

for block in final_message.content:
    if block.type == "text":
        print(block.text)