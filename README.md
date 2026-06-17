# Copilot for Lawyers — AI-Powered Contract Review System

A proof of concept built for the course **194.211 Applied Generative AI and LLM-based Systems** at TU Wien (2026S).

The system allows legal professionals to upload contracts, automatically detect risky clauses, check compliance with GDPR and DORA, rewrite problematic clauses, and search semantically across multiple indexed documents.

---

## Setup

### Prerequisites

- Python 3.10 or higher (note: Python 3.13 is supported but PyTorch is not available for it — the system uses ChromaDB's built-in embedding model instead of sentence-transformers)
- A Groq API key (free tier available at https://console.groq.com)

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/KhristinaVasko/Co-Pilot_for_Lawyers.git
cd Co-Pilot_for_Lawyers
pip install -r requirements.txt
```

If you do not have a `requirements.txt` yet, install manually:

```bash
pip install streamlit pymupdf groq chromadb rapidfuzz
```

### API Key

Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY=your_groq_key_here
```

Alternatively, open `app.py` and replace the placeholder in this line:

```python
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_groq_key_here")
```

### Running the Application

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## Application Overview

The application has three main views, selectable from the left sidebar: **Contract Review**, **Risk Overview**, and **Document Search**.

---

## Contract Review

This is the primary view for analysing a single uploaded contract.

### Uploading and Analysing a Contract

1. Click the upload area at the top and select a PDF contract.
2. The system reads the PDF using PyMuPDF and extracts all text.
3. The clause extractor identifies individual clauses using numbered section patterns (e.g. "1. Scope of Services", "2. Payment Terms"). Clauses numbered 1 through 20 are detected.
4. Click **Analyze** to start the analysis. Each clause is sent individually to the Groq API (Llama 3.3 70B) with a system prompt that defines the risk categories to look for.
5. For each clause the model returns a structured JSON object containing the risk level (none / low / medium / high), the risk category, the exact risky excerpt from the clause, an explanation, and references to relevant GDPR or DORA articles where applicable.

### Risk Dashboard

After analysis, five metric cards appear at the top:

- **Total risks** — total number of clauses flagged at any risk level
- **High risk** — number of high-severity clauses
- **Medium risk** — number of medium-severity clauses
- **GDPR violations** — number of clauses with a detected GDPR article reference
- **DORA violations** — number of clauses with a detected DORA article reference

### Clause List

The left column shows all detected clauses. Each card displays:

- The clause title
- A short preview of the identified risk
- Colour-coded badges: **GDPR** (purple), **DORA** (green), and a risk level badge (red for HIGH, amber for MED, blue for LOW)
- A **Details →** button for risky clauses

### Clause Detail Panel

Clicking **Details →** opens the right-hand detail panel for that clause. The panel has four tabs:

**Risk tab**
Shows the risk category, the exact risky excerpt highlighted in the appropriate colour, and a plain-language explanation of why the clause is problematic.

**GDPR / DORA tab**
Shows any GDPR or DORA article violations detected during the initial analysis, displayed as colour-coded cards (red for GDPR, green for DORA). A **Run full GDPR/DORA analysis** button triggers a deeper analysis using the full GDPR and DORA article context embedded in the system, returning a detailed breakdown of all relevant articles.

**Rewrite tab**
Click **Generate rewrite** to ask the model to produce a safer, more balanced version of the selected clause. The rewritten clause is displayed below and can be copied manually.

**Agent chat tab**
Each clause has its own independent chat history. You can ask follow-up questions about the specific clause, such as:

- "Why is this clause high risk?"
- "Which GDPR articles does this violate?"
- "Rewrite clause 3 to be GDPR compliant"
- "If I am the client, how should I negotiate this?"

The chat uses an agentic architecture with tool calling. The agent autonomously decides which tool to invoke based on your question. Available tools include clause retrieval, clause rewriting, GDPR/DORA regulatory analysis, risk summary, and semantic contract search. The tool used is shown below each response.

Chat history is preserved per clause — if you switch to another clause and return, your previous conversation is still there.

### Highlighted Contract

At the bottom of the page, the full contract text is displayed with all risky excerpts highlighted. Colours correspond to risk level: red for high, amber for medium, blue for low. Hovering over a highlighted passage shows the risk category and explanation as a tooltip. When you select a clause using **Details →**, the highlighted contract automatically scrolls to and outlines that clause.

---

## Risk Overview

This view aggregates the risk analysis of **every analysed document into a single cross-document table**, so reviewers can compare risk level, category and confidence across a whole portfolio of contracts at once rather than one document at a time.

### How risk data is persisted

Risk analysis was previously held only in session state for the contract currently being reviewed. Each analysis is now also written to `./risk_analysis/<filename>.json` — both when a single contract is analysed in **Contract Review** and when contracts are analysed in bulk here. The Risk Overview view loads all of those files and aggregates them.

### Populating the table

- **Analyze all contracts** — point the folder field at a directory of PDFs (defaults to `sample_contracts`) and click the button. Every PDF is read, split into clauses, indexed into the vector store, and risk-analysed clause by clause, with a progress bar across files and clauses. Each document's results are saved to disk.
- Any contract analysed individually in **Contract Review** also appears here automatically.

### The cross-document table

The table has one row per flagged clause with the columns **Document**, **Clause**, **Risk**, **Category**, **Confidence**, **GDPR**, **DORA**, and **Page**. The risk and confidence cells are colour-coded (red / amber / blue for high / medium / low risk; green / amber / grey for found / uncertain / not-specified confidence). Rows are sorted by severity.

Above the table, summary metrics show the number of documents, high / medium / low risk counts, and GDPR / DORA reference counts across all documents. Two filters let you narrow the table by document and by risk level (no-risk clauses are hidden by default). The filtered table can be exported with **Download CSV**.

---

## Document Search

This view enables semantic search across multiple indexed contracts simultaneously.

### Indexing Contracts

1. Ensure your PDF contracts are in the `./sample_contracts` folder (or change the folder path in the input field).
2. Click **Index all contracts**. The system reads each PDF, extracts clauses, generates vector embeddings using ChromaDB's built-in embedding model (all-MiniLM-L6-v2), and stores each clause with metadata (filename, clause number, clause title) in a local ChromaDB database.
3. The sidebar shows the list of indexed documents and the total number of clauses in the database.

### How RAG Works

The system uses Retrieval-Augmented Generation (RAG) to answer questions across all indexed contracts without sending every document to the language model at once.

When you submit a search query or a chat message, the system:

1. Converts your query into a vector embedding using the same model used during indexing.
2. Queries ChromaDB to find the most semantically similar clause vectors.
3. Returns the top matching clauses with their similarity scores, filenames, and clause titles.
4. Passes the retrieved clauses as context to the language model, which synthesises an answer grounded in the actual contract text.

This means the system can answer questions like "which documents have the most problematic termination clauses?" or "does the employment contract comply with GDPR?" by searching across all 49 indexed clauses from six documents simultaneously, without needing to analyse each document individually every time.

### Semantic Search

Type a search query in the search box. Results are displayed as expandable cards showing the source filename, clause title, similarity score (colour-coded: green above 0.6, amber above 0.4, red below), and the full clause text.

Example queries:

- `termination without notice`
- `data breach notification`
- `liability cap`
- `automatic renewal`

### Cross-Document Agent Chat

Below the search results, a chat interface allows you to ask questions that span all indexed documents. The agent uses the `search_contract` tool to retrieve relevant clauses from ChromaDB and synthesises answers across multiple documents. Example questions:

- "Which documents have the most problematic termination clauses?"
- "Does the employment contract comply with GDPR?"
- "Which contracts are missing incident reporting obligations required by DORA?"
- "Compare the liability clauses across all documents — which one is most risky?"

---

## Regulatory Grounding

The system is grounded in the following regulatory frameworks, embedded directly in the model's system context:

**GDPR articles:** 28 (Processor obligations), 33 (Data breach notification), 46 (Transfers outside EEA), 82 (Right to compensation)

**DORA articles:** 19 (Reporting of major ICT incidents), 28 (ICT third-party risk), 30 (Key contractual provisions)

These article texts are included in the prompts so the model can cite specific requirements rather than relying solely on general knowledge. As noted in the limitations below, the model's interpretation of these articles should not be treated as certified legal advice.

---

## Limitations

**Clause segmentation** depends on numbered formatting conventions. Contracts with unusual or inconsistent structure (e.g. unnumbered paragraphs, Roman numerals, non-standard headings) may not be segmented correctly.

**Risk categories** were defined by the development team based on general legal knowledge and publicly available contract review guides, not by certified legal professionals. The system may miss domain-specific risks or flag clauses that are unproblematic in specific legal contexts.

**RAG does not include pre-computed risk analysis.** When contracts are indexed into ChromaDB, only the raw clause text is stored — not the risk analysis results. The cross-document agent chat uses semantic search to find relevant clauses, but it does not have access to pre-computed risk levels for each indexed document. A full risk analysis (high / medium / low ratings, GDPR/DORA flags) is only available for the single contract uploaded in the Contract Review tab. Performing a full analysis across all indexed documents simultaneously would require one LLM call per clause, which for six documents with roughly 40 clauses total would mean 40+ sequential API calls. This was not implemented in the current proof of concept due to latency and API usage constraints.

**Language support** is limited to English. The clause extractor uses patterns designed for English legal document formatting, and the risk analysis prompts are written in English.

**Model reliability.** While large language models have been exposed to legal and regulatory texts during training, they do not guarantee correctness or up-to-date interpretation. All outputs should be reviewed by a qualified legal professional. The system is a decision-support tool, not a substitute for professional legal advice.

**Groq rate limits.** The free tier of the Groq API has daily and per-minute request limits. Analysing a contract with 10 clauses requires 10 API calls. For larger contracts or repeated use, rate limit errors may occur.

---

## Tech Stack

| Component | Tool |
|---|---|
| Language model | Llama 3.3 70B via Groq API |
| PDF parsing | PyMuPDF (fitz) |
| Vector database | ChromaDB (local, persistent) |
| Embeddings | all-MiniLM-L6-v2 (built into ChromaDB) |
| Web interface | Streamlit |
| Fuzzy matching | rapidfuzz |
| Language | Python 3.10+ |

---

## Project Structure

```
copilot_lawyers/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── sample_contracts/       # Sample PDF contracts for testing
│   ├── 01_Service_Agreement_DataFlow_LegalCorp.pdf
│   ├── 02_Employment_Contract_RiverTech.pdf
│   ├── 03_NDA_NovaMed_InsightBridge.pdf
│   ├── 04_SaaS_Subscription_CloudLedger.pdf
│   ├── 05_Data_Processing_Agreement_MedStore.pdf
│   └── 06_Equipment_Lease_Agreement_OfficeMachines.pdf
├── contract_db/            # ChromaDB local database (auto-generated, not tracked in git)
└── risk_analysis/          # Per-document risk analysis JSON, powers Risk Overview (auto-generated, not tracked in git)
```

---

## Group

TU Wien — 194.211 Applied Generative AI and LLM-based Systems, 2026S
