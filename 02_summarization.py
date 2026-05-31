# 02_summarization.py
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def summarize(text: str, style: str = "bullet points") -> str:
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Summarize the following text in {style}:\n\n{text}"
        }]
    )
    return message.content[0].text

if __name__ == "__main__":
    sample = """
    The Apollo program was a series of NASA spaceflight missions that landed the first
    humans on the Moon. Between 1969 and 1972, six missions successfully landed astronauts
    on the lunar surface. Neil Armstrong and Buzz Aldrin became the first humans to walk
    on the Moon on July 20, 1969, during Apollo 11. The program is considered one of the
    greatest achievements in human history and a defining moment of the 20th century.
    """
    print(summarize(sample))
