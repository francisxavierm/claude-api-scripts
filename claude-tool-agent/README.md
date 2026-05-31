# Claude Tool Agent

A command-line assistant powered by the Anthropic API that can search the web, read local files, and write local files.

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key (https://console.anthropic.com)
- A Tavily API key (https://app.tavily.com)


## Quickstart

1. Clone the repo
   git clone https://github.com/francisxavierm/claude-api-scripts.git
   cd claude-api-scripts/claude-tool-agent

2. Install dependencies
   pip install -r requirements.txt

3. Set your API keys
   cp .env.example .env
   Then open .env and fill in your real keys.

4. Run the assistant
   python -m src.cli


## How It Works

When you type a message, Claude decides which tools to use.
It calls the tool, gets the result, and keeps going until
it has enough information to give you a final answer.

The loop looks like this:

1. You send a message
2. Claude calls a tool (web search, read file, or write file)
3. Your code runs the tool and sends the result back
4. Claude either calls another tool or gives a final answer


## Troubleshooting

**ModuleNotFoundError: No module named 'src'**
Run the project from inside the claude-tool-agent folder using:
python -m src.cli

**AuthenticationError**
Your API key is not loading. Run this to check:
echo $ANTHROPIC_API_KEY
If it shows blank, run:
export $(cat .env | xargs)

