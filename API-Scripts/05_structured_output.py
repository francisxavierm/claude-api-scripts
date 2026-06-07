# 05_structured_output.py
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Define the schema as a tool so Claude is forced to use it
product_review_tool = {
    "name": "save_review_analysis",
    "description": "Save the structured analysis of a product review.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment":    {"type": "string", "enum": ["positive", "neutral", "negative"]},
            "rating":       {"type": "integer", "minimum": 1, "maximum": 5},
            "pros":         {"type": "array", "items": {"type": "string"}},
            "cons":         {"type": "array", "items": {"type": "string"}},
            "summary":      {"type": "string"}
        },
        "required": ["sentiment", "rating", "pros", "cons", "summary"]
    }
}

def analyze_review(review_text: str) -> dict:
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        tools=[product_review_tool],
        tool_choice={"type": "tool", "name": "save_review_analysis"},
        messages=[{
            "role": "user",
            "content": f"Analyze this product review:\n\n{review_text}"
        }]
    )
    # Tool use response is in content[0].input
    return response.content[0].input

if __name__ == "__main__":
    review = """
    I've been using these headphones for two months. The sound quality is absolutely
    incredible — rich bass and crystal-clear highs. Battery lasts a full 30 hours.
    However, the ear cushions started peeling after just 6 weeks, and the carrying
    case feels very cheap for a $150 product. The app also crashes occasionally.
    Overall still happy with the purchase but the build quality is disappointing.
    """
    result = analyze_review(review)
    print(json.dumps(result, indent=2))
