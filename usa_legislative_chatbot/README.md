# 🏛️ USA Legislative Chatbot

A document-grounded Q&A chatbot that answers questions about US federal legislation — bill provisions, CBO scores, Senate rules, and legislative procedures — using Retrieval-Augmented Generation (RAG) with Claude as the language model.

**Live app:** [Add your Streamlit URL here]

---

## Case Study

### 1. Problem

US federal legislation is publicly available but practically inaccessible. A single major bill like the Inflation Reduction Act runs to over 700 pages. CBO cost estimates use dense budget terminology. CRS analyses assume Congressional-level expertise. A citizen, journalist, student, or policy researcher trying to find a specific provision, a cost figure, or a procedural rule has to manually search through enormous PDFs spread across multiple government websites — congress.gov, cbo.gov, gao.gov, everycrsreport.com — with no unified interface.

The core problem is not access — all these documents are free and public — it is navigability. A document-grounded chatbot that ingests the actual PDFs, indexes them semantically, and retrieves exact passages solves this. Every answer is traceable to a source document, making it verifiable rather than a black-box response from a language model's training memory.

---

### 2. Approach

**Domain and documents**
36 PDFs were collected entirely from free government sources — congress.gov, cbo.gov, everycrsreport.com, senate.gov, and house.gov — with no login, paywall, or scraping required. The collection covers four categories: major bill texts (Inflation Reduction Act, CHIPS Act, Infrastructure Act, American Rescue Plan, Fiscal Responsibility Act, NDAA FY2024, Consolidated Appropriations Act 2023), CBO cost estimates for each bill, Congressional Research Service analyses on budget reconciliation, filibusters, cloture, the Congressional Review Act, and legislative procedure, and rules manuals for both the Senate and House of Representatives.

**PDF extraction**
`pypdf` was used to extract text from all 36 PDFs. All congress.gov and government PDFs are text-native — no OCR was needed. Text was extracted page by page and joined into a single string per document before chunking.

**Chunking strategy**
Chunk size was set to 512 tokens with 64 tokens of overlap, using OpenAI's `cl100k_base` tokeniser via `tiktoken`. 512 tokens was chosen because it typically captures one complete legislative provision or CBO table row without splitting mid-clause. At 256 tokens, provisions were frequently split mid-sentence. At 1024 tokens, a single chunk covered too many unrelated provisions, degrading retrieval precision. The 64-token overlap ensures sentences at chunk boundaries appear fully in at least one chunk.

**Embedding and vector storage**
Chroma's `DefaultEmbeddingFunction` was used, which wraps `sentence-transformers/all-MiniLM-L6-v2`. This model runs locally on CPU, costs nothing per embedding, and handles formal English legislative text well. It produces 384-dimensional vectors. Chroma stores both the chunk text and the embedding vectors on disk in `chroma_db/`, which is rebuilt at app startup on Streamlit Cloud using `@st.cache_resource`.

**Retrieval**
TOP_K was set to 5 — retrieving the 5 most semantically similar chunks for each query. Initial testing with TOP_K=3 missed CBO cost figures that ranked 4th or 5th in similarity. TOP_K=7 occasionally introduced irrelevant chunks from tangentially related documents. 5 was the best balance between context richness and retrieval noise.

**Language model**
`claude-haiku-4-5-20251001` was used for answer generation. For a factual retrieval task where the model is essentially doing reading comprehension over retrieved passages, Haiku is sufficient and significantly cheaper than Sonnet. The system prompt instructs Claude to cite source filenames and exact figures, and to respond with "This information is not in my knowledge base" for out-of-scope questions.

**Preprocessing**
All PDFs were renamed from cryptic government filenames (e.g. `BILLS-117hr5376enr.pdf`) to descriptive names (e.g. `Inflation Reduction Act 2022.pdf`) before ingestion, so source citations in answers are human-readable. One duplicate NDAA file was retained as both versions contained unique sections.

---

### 3. Results

The chatbot was tested against the 10 sample questions defined before building. All answers were verified against the source PDFs.

**Q1: What does the Inflation Reduction Act say about Medicare drug price negotiation?**
> The Inflation Reduction Act establishes a Fair Price Negotiation Program under which the Secretary of Health and Human Services shall negotiate drug prices directly with manufacturers for a selected list of high-expenditure Medicare drugs. The first 10 drugs subject to negotiation were to be selected by 2023, with negotiated prices taking effect in 2026. [Source: Inflation Reduction Act 2022.pdf, Negotiation of Drug Prices in Medicare Part D.pdf]

Assessment: Correct. Both the bill text and the CRS analysis were retrieved and synthesised accurately.

---

**Q2: What was the CBO score for the American Rescue Plan Act of 2021?**
> According to the CBO cost estimate, the American Rescue Plan Act of 2021 would increase the federal deficit by approximately $1.9 trillion over the 2021–2031 period. The largest single component was $1 trillion in direct payments and unemployment insurance extensions. [Source: CBO score — American Rescue Plan 2021.pdf]

Assessment: Correct. Exact figure cited from the correct CBO document.

---

**Q3: How is cloture invoked to end a filibuster in the US Senate?**
> Under Senate Rule XXII, cloture can be invoked by a vote of three-fifths of the full Senate membership — typically 60 senators. A cloture motion must be signed by at least 16 senators and filed with the presiding officer. The vote occurs two days after the motion is filed. Once cloture is invoked, debate is limited to an additional 30 hours before a final vote must occur. [Source: Filibusters and Cloture in the Senate.pdf, SENATE MANUAL.pdf]

Assessment: Correct. Specific rule cited with accurate procedural details.

---

**Q4: What did the CHIPS and Science Act allocate for semiconductor manufacturing?**
> The CHIPS and Science Act of 2022 allocated approximately $52 billion for domestic semiconductor manufacturing and research, including $39 billion in manufacturing incentives, $13.2 billion for semiconductor research and development, and $500 million for international partnerships on semiconductor supply chains. [Source: CHIPS and Science Act 2022.pdf, CBO score — CHIPS and Science Act 2022.pdf]

Assessment: Correct. Dollar breakdown retrieved from both the bill and CBO estimate.

---

**Q5: How does the Congressional Review Act work?**
> The Congressional Review Act (CRA) allows Congress to review and potentially overturn new federal agency rules before they take effect. Under the CRA, agencies must submit final rules to Congress before they can take effect. Congress then has 60 legislative days to pass a joint resolution of disapproval. If both chambers pass the resolution and the President signs it — or if Congress overrides a veto — the rule is nullified and the agency is prohibited from issuing a substantially similar rule without new legislative authorisation. [Source: The Congressional Review Act CRA - A Brief Overview.pdf]

Assessment: Correct. Complete procedural description with the 60-day window and re-issuance prohibition.

---

**Out-of-scope test**

**Q: Who won the FIFA World Cup in 2022?**
> This information is not in my knowledge base. I can only answer questions about US federal legislation from the 115th to 119th Congress (2017–2025).

Assessment: Correct behaviour. Claude did not fall back on its training data.

---

**Failure case observed**

A question about the Consolidated Appropriations Act 2023's specific line items for housing programmes initially returned chunks from the Budget Control Act of 2011 instead, because both documents contain budget ceiling language. Increasing TOP_K to 7 for that query resolved the issue. This revealed that for very long omnibus bills, broader retrieval improves precision.

---

### 4. Cost Per Query

Pricing for `claude-haiku-4-5-20251001`:
- Input: $0.80 per million tokens
- Output: $4.00 per million tokens

Typical query breakdown for this knowledge base:

| Component | Tokens |
|---|---|
| System prompt | ~150 |
| 5 chunks × ~500 tokens | ~2,500 |
| User question | ~20 |
| **Total input** | **~2,670** |
| Answer output | ~280 |

```
Input cost  = (2,670 / 1,000,000) × $0.80 = $0.00214
Output cost = (  280 / 1,000,000) × $4.00 = $0.00112
Cost per query                             ≈ $0.00326
```

| Scale | Haiku cost | Sonnet cost (est.) |
|---|---|---|
| 100 queries | $0.33 | $1.30 |
| 1,000 queries | $3.26 | $13.00 |
| 10,000 queries | $32.60 | $130.00 |

Haiku was sufficient for this task. Legislative Q&A is fundamentally reading comprehension — Claude reads 5 retrieved passages and writes a cited summary. This does not require Sonnet's deeper reasoning capability. Sonnet would be worth the cost for tasks requiring cross-document synthesis, legal interpretation, or multi-step reasoning across many provisions simultaneously.

---

## Tech Stack

| Component | Tool |
|---|---|
| PDF extraction | pypdf |
| Tokenisation | tiktoken (cl100k_base) |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 |
| Vector database | ChromaDB (persistent, local) |
| Language model | claude-haiku-4-5-20251001 |
| UI framework | Streamlit |
| Deployment | Streamlit Community Cloud |

---

## Project Structure

```
usa_legislative_chatbot/
├── data/
│   └── raw_pdfs/          # 36 source PDFs from government websites
├── src/
│   ├── ingest.py          # PDF extraction → chunking → Chroma upsert
│   ├── retrieval.py       # Chroma query → prompt build → Claude API
│   ├── app.py             # Streamlit UI
│   └── requirements.txt   # Python dependencies
├── chroma_db/             # Auto-generated vector store (gitignored)
├── runtime.txt            # Python 3.11 for Streamlit Cloud
└── .gitignore
```

---

## PDF Sources

All 36 PDFs were downloaded free from:
- **congress.gov** — full bill texts
- **cbo.gov** — cost estimates and budget outlooks
- **everycrsreport.com** — Congressional Research Service analyses
- **senate.gov** — Senate Rules Manual
- **house.gov** — House Rules Manual

No login, paywall, or scraping was used.

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/claude-api-scripts.git
cd claude-api-scripts/usa_legislative_chatbot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Ingest PDFs (run once)
python src/ingest.py

# Launch the app
streamlit run src/app.py
```

---

## Week 3 Deliverable — RAG Chatbot

Built as part of a structured AI implementation curriculum. Domain: US federal legislation (115th–119th Congress, 2017–2025).
