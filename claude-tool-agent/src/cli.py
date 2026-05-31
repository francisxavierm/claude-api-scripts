# src/cli.py
import sys
from dotenv import load_dotenv
from src.agent import run_agent
load_dotenv() # loads .env into environment variables
def main():
    print("Claude Tool Agent (type 'quit' to exit)\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            sys.exit(0)
        print("\nClaude: ", end="", flush=True)
        response = run_agent(user_input, verbose=True)
        print(response)
        print()
if __name__ == "__main__":
    main()