# 03_classification.py
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

CATEGORIES = ["Technology", "Sports", "Politics", "Entertainment", "Science", "Other"]

def classify(text: str) -> str:
    categories_str = ", ".join(CATEGORIES)
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        messages=[{
            "role": "user",
            "content": (
                f"Classify the following text into exactly one of these categories: {categories_str}.\n"
                f"Reply with only the category name, nothing else.\n\nText: {text}"
            )
        }]
    )
    return message.content[0].text.strip()

if __name__ == "__main__":
    samples = [
        "NASA just announced a new mission to Mars launching in 2028.",
        "The Lakers defeated the Celtics in a thrilling overtime game last night.",
        "The new smartphone features a 200MP camera and 7000mAh battery.",
    ]
    for sample in samples:
        label = classify(sample)
        print(f"[{label}] {sample[:60]}...")
