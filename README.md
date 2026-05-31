# Claude API Scripts

Five minimal Python scripts demonstrating core Claude API patterns.

## Scripts

| File | What it does |
|------|-------------|
| `01_text_generation.py` | Open-ended text generation from a prompt |
| `02_summarization.py` | Summarize long text into bullet points or prose |
| `03_classification.py` | Classify text into predefined categories |
| `04_json_extraction.py` | Extract structured JSON from unstructured text |
| `05_structured_output.py` | Enforce strict output schema via tool use |

## Setup

\```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your API key
\```

Get an API key at https://console.anthropic.com/

## Usage

Each script runs standalone:

\```bash
python3 01_text_generation.py
python3 02_summarization.py
# etc.
\```
