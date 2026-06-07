import fitz # PyMuPDF
import pathlib, tiktoken, chromadb
from chromadb.utils import embedding_functions

CHUNK_SIZE = 512 # tokens — captures one legislative provision
CHUNK_OVERLAP = 64 # tokens — preserves cross-sentence context
COLLECTION = 'usa_legislative_kb'
DB_PATH = './chroma_db'

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION, embedding_function=ef
    )

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text('text')
        if text.strip():
            pages.append(text)
    return '\n'.join(pages)

def chunk_text(text: str, source: str) -> list[dict]:
    enc    = tiktoken.get_encoding('cl100k_base')
    tokens = enc.encode(text)
    chunks, start = [], 0
    while start < len(tokens):
        end   = min(start + CHUNK_SIZE, len(tokens))
        chunk = enc.decode(tokens[start:end])
        chunks.append({
            'text'    : chunk,
            'source'  : source,
            'chunk_id': f'{source}::{start}',
        })
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def ingest_chunks(chunks: list[dict]) -> None:
    col = get_collection()
    col.upsert(
        ids       = [c['chunk_id'] for c in chunks],
        documents = [c['text']     for c in chunks],
        metadatas = [{'source': c['source']} for c in chunks],
    )

def ingest_all(pdf_dir: str = 'data/raw_pdfs') -> None:
    paths = list(pathlib.Path(pdf_dir).glob('**/*.pdf'))
    print(f'Found {len(paths)} PDFs')
    for path in paths:
        print(f' Processing: {path.name}')
        text = extract_text(str(path))
        chunks = chunk_text(text, source=path.name)
        ingest_chunks(chunks)
        print(f' Chunks: {len(chunks)}')
        print(f'Done. Total chunks: {get_collection().count()}')
if __name__ == '__main__':
    ingest_all()