# src/agent.py
from urllib import response

from urllib import response

import anthropic
from src.tools import TOOL_SCHEMAS, execute_tool

MODEL = "claude-opus-4-6"
MAX_TOKENS = 4096

def run_agent(user_message: str, verbose: bool = True) -> str:
    """
    Run a single user turn through the tool-use loop.
    Returns the final text response from Claude.
    """
    client = anthropic.Anthropic()
    # Seed the conversation with the user's message
    messages = [{"role": "user", "content": user_message}]

    while True:
        # ── Call the API
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=TOOL_SCHEMAS,
            messages=messages
        )
        if verbose:
            print(f"\n[stop_reason: {response.stop_reason}]")

        # ── End of conversation

        if response.stop_reason == "end_turn":
            # Extract the final text block
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "" # no text block (shouldn't happen)
        
        # ── Tool use requested

        if response.stop_reason == "tool_use":
        # 1. Add Claude's response to the message history
        messages.append({"role": "assistant", "content": response.content})

        # 2. Execute every tool Claude requested in this turn
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if verbose:
                    print(f"[tool_call] {block.name}({block.input})")
                result = execute_tool(block.name, block.input)

                if verbose:
                    preview = result[:200] + "…" if len(result) > 200 else result
                    print(f"[tool_result] {preview}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # 3. Append all tool results as a single user message
        messages.append({"role": "user", "content": tool_results})

        # 4. Loop — call the API again with the updated history
        continue

    # ── Unexpected stop_reason
    raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")