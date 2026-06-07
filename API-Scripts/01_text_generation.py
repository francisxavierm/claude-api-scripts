# 01_text_generation.py
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def generate_text(prompt: str, max_tokens: int = 512) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

if __name__ == "__main__":
    print("Claude Text Generator")
    print("---------------------")
    prompt = input("Enter your prompt: ").strip()

    if not prompt:
        print("No prompt entered. Exiting.")
    else:
        print("\nGenerating...\n")
        result = generate_text(prompt)
        print(result)
