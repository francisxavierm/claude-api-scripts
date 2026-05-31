# 04_json_extraction.py
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def extract_json(text: str, schema_description: str) -> dict:
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                f"Extract the following information from the text and return ONLY valid JSON "
                f"with no explanation:\nSchema: {schema_description}\n\nText: {text}"
            )
        }]
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)

if __name__ == "__main__":
    text = """
    John Smith placed an order on March 15, 2025. He ordered 3 units of 'Pro Wireless
    Headphones' at $89.99 each. His shipping address is 42 Maple Street, Austin, TX 78701.
    The order ID is ORD-20250315-8821.
    """
    schema = "{ order_id, customer_name, date, items: [{name, quantity, unit_price}], shipping_address }"
    result = extract_json(text, schema)
    print(json.dumps(result, indent=2))
