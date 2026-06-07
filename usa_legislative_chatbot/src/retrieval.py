import os, anthropic, sys, pathlib
from dotenv import load_dotenv
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ingest import get_collection

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
TOP_K = 5

def retrieve(query: str) -> list[dict]:
    col     = get_collection()
    results = col.query(query_texts=[query], n_results=TOP_K)
    return [
        {'text': doc, 'source': meta['source']}
        for doc, meta in zip(results['documents'][0],
                             results['metadatas'][0])
    ]

def build_prompt(query: str, chunks: list[dict]) -> str:
    context = '\n\n'.join(
        f'[Source {i}: {c["source"]}]\n{c["text"]}'
        for i, c in enumerate(chunks, 1)
    )
    return f'''You are an expert assistant on US federal egislation covering the 115th to 119th Congress (2017–2025).
    Answer the user's question using ONLY the context below.
    Rules:
    - Cite the source filename and relevant section for every fact.
    - For dollar amounts, quote the exact figure from the document.
    - For procedural questions, cite the specific rule or statute.
    - If the answer is not in the context, say:
    'This information is not in my knowledge base.'
    - Do not speculate or use outside knowledge.
    CONTEXT:
    {context}

    QUESTION: {query}

    ANSWER:'''

def answer(query: str) -> dict:
    chunks  = retrieve(query)
    message = client.messages.create(
        model      = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        messages   = [{'role': 'user',
                       'content': build_prompt(query, chunks)}],
    )
    return {
        'answer'       : message.content[0].text,
        'sources'      : [c['source'] for c in chunks],
        'total_tokens' : (message.usage.input_tokens +
                          message.usage.output_tokens),
    }

if __name__ == '__main__':
 tests = [
    'What does the Inflation Reduction Act say about Medicare drug pricing?',
    'How is cloture invoked in the US Senate?',
    'What was the CBO cost estimate for the American Rescue Plan?',
 ]
 for q in tests:
    print(f'\nQ: {q}')
    r = answer(q)
    print(f'A: {r["answer"]}')
    print(f'Sources: {r["sources"]}')
    print(f'Tokens: {r["total_tokens"]}')