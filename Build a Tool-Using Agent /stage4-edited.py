import json
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

@beta_tool
def create_calendar_event(
    title: str,
    start: str,
    end: str,
    attendees: list[str] | None = None
) -> str:
    """Create a calendar event. Maximum 3 attendees.

    Args:
        title: Event title.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        attendees: Email addresses to invite.
    """
    attendees = attendees or []

    # Same limit as Stage 4 — triggers the error path
    if len(attendees) > 3:
        raise ValueError(f"Too many attendees ({len(attendees)}) — maximum is 3.")

    print(f"  Creating event: {title} with {len(attendees)} attendee(s)")
    return json.dumps({"event_id": "evt_123", "status": "created"})

# Same prompt as Stage 4 — 5 people to trigger the limit
final_message = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[create_calendar_event],
    messages=[{
        "role": "user",
        "content": (
            "Schedule a team lunch for tomorrow at noon with "
            "alice@work.com, bob@work.com, carol@work.com, dave@work.com, eve@work.com."
        )
    }]
).until_done()

final = next(block for block in final_message.content if block.type == "text")
print("\nFinal answer:", final.text)