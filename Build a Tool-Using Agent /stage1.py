# stage1.py
import json
import anthropic

# Step 1: Connect to the API
client = anthropic.Anthropic()

# Step 2: Describe your tool to Claude.
# This is NOT the Python function — it's just a description in JSON
# that tells Claude "this tool exists, and here's what it takes."

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

# Step 3: Send the user's message along with the tool description.
response = client.messages.create(
 	model="claude-opus-4-6",
 	max_tokens=1024,
 	tools=tools,
	messages=[{
 		"role": "user",
 		"content": "Schedule a 30-minute sync with alice@work.com and bob@work.com next Monday at 10am."
 	}]
)

# Step 4: See what Claude returned.
print("stop_reason:", response.stop_reason)
# Expected: "tool_use" — Claude wants to call a tool

# Step 5: Find the tool call inside Claude's response.
# Claude's response can have multiple content blocks (text + tool calls).
# We scan for the one with type "tool_use".
tool_use = next(block for block in response.content if block.type == "tool_use")
print("Tool Claude wants to call:", tool_use.name)
print("Arguments Claude chose: ", tool_use.input)
# tool_use.id is a unique ID we must reference when sending the result back

# Step 6: "Execute" the tool.
# In a real app this would call your calendar API.
# For now we fake a successful result.
result = {"event_id": "evt_123", "status": "created"}

# Step 7: Send the result back to Claude.
# We rebuild the full conversation: original question → Claude's response → ourresult.
followup = client.messages.create(
 	model="claude-opus-4-6",
 	max_tokens=1024,
 	tools=tools,
 	messages=[
 		# The original user message
 		{
 			"role": "user",
 			"content": "Schedule a 30-minute sync with alice@work.com and bob@work.com next Monday at 10am."
 		},
 		# Claude's response (which contained the tool call)
 		{
 			"role": "assistant",
 			"content": response.content
 		},
 		# Our tool result — must include the matching tool_use_id
 		{
 			"role": "user",
 			"content": [{
 				"type": "tool_result",
 				"tool_use_id": tool_use.id, # ← must match the id from Step 5
 				"content": json.dumps(result)
 			}]
 		}
 	]
)

# Step 8: See the final answer.
print("\nstop_reason:", followup.stop_reason)
# Expected: "end_turn" — Claude is done
final = next(block for block in followup.content if block.type == "text")
print("Claude says:", final.text)
