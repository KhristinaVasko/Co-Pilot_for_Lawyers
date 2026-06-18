# Copilot for Lawyers — AI-Powered Contract Review System

A proof of concept built for the course **194.211 Applied Generative AI and LLM-based Systems** at TU Wien (2026S).

The system allows legal professionals to upload contracts, automatically detect risky clauses, check compliance with GDPR and DORA, rewrite problematic clauses, and search semantically across multiple indexed documents.

---

## Setup

### Prerequisites

Python 3.10 or higher (note: Python 3.13 is supported but PyTorch is not available for it — the system uses ChromaDB's built-in embedding model instead of sentence-transformers)

A Groq API key (free tier available at https://console.groq.com)

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/KhristinaVasko/Co-Pilot_for_Lawyers.git
cd Co-Pilot_for_Lawyers
pip install -r requirements.txt
```

### API Key

Copy the example env file and add your key:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your Groq API key. Get a free key at https://console.groq.com

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
2. The system reads the PDF using PyMuPDF and extracts all text page by page.
3. The clause extractor identifies individual clauses using numbered section patterns (e.g. "1. Scope of Services", "2. Payment Terms"). Clauses numbered 1 through 20 are detected, as well as formal legal markers such as ARTICLE, Section, and SCHEDULE.
4. Click **Analyze** to start the analysis. Each clause is sent individually to the Groq API (Llama 3.3 70B) with a system prompt that defines the risk categories to look for.
5. For each clause the model returns a structured JSON object containing the risk level (none / low / medium / high), the risk category, the exact risky excerpt from the clause, an explanation, and references to relevant GDPR or DORA articles where applicable.

### Risk Dashboard

After analysis, five metric cards appear at the top:

| Metric | Description |
|---|---|
| Total risks | Total number of clauses flagged at any risk level |
| High risk | Number of high-severity clauses |
| Medium risk | Number of medium-severity clauses |
| GDPR violations | Number of clauses with a detected GDPR article reference |
| DORA violations | Number of clauses with a detected DORA article reference |

### Clause List

The left column shows all detected clauses. Each card displays the clause title, a short preview of the identified risk, and colour-coded badges: **GDPR** (purple), **DORA** (green), and a risk level badge (red for HIGH, amber for MED, blue for LOW). Risky clauses have a **Details →** button.

### Clause Detail Panel

Clicking **Details →** opens the right-hand detail panel for that clause. The panel has four tabs:

**Risk tab**
Shows the risk category, the exact risky excerpt highlighted in the appropriate colour, and a plain-language explanation of why the clause is problematic. A confidence badge indicates whether the risk was clearly identified (Confirmed risk), ambiguous (Uncertain — review manually), or absent from the clause entirely (Not specified in clause).

**GDPR / DORA tab**
Shows any GDPR or DORA article violations detected during the initial analysis. A **Run full GDPR/DORA analysis** button triggers a deeper analysis using the full article text embedded in the system prompt, returning a detailed breakdown of all relevant articles.

**Rewrite tab**
Click **Generate rewrite** to ask the model to produce a safer, more balanced version of the selected clause.

**Agent chat tab**
Each clause has its own independent chat history. You can ask follow-up questions such as "Why is this clause high risk?", "Which GDPR articles does this violate?", or "Rewrite this to be GDPR compliant". The agent uses tool calling and autonomously decides which tool to invoke. The tool used is shown below each response. Chat history is preserved per clause.

### Highlighted Contract

At the bottom of the page, the full contract text is displayed with all risky excerpts highlighted in colours corresponding to risk level. Hovering over a highlighted passage shows the risk category and explanation as a tooltip.

---

## Risk Overview

This view aggregates the risk analysis of every analysed document into a single cross-document table, so reviewers can compare risk level, category and confidence across a whole portfolio of contracts at once.

### How Risk Data is Persisted

Each analysis is written to `./risk_analysis/<filename>.json` both when a single contract is analysed in Contract Review and when contracts are analysed in bulk here. The Risk Overview view loads all of those files and aggregates them into one table.

### Populating the Table

Point the folder field at a directory of PDFs (defaults to `./sample_contracts`) and click **Analyze all contracts**. Every PDF is read, split into clauses, indexed into the vector store, and risk-analysed clause by clause with a progress bar across files and clauses. Any contract analysed individually in Contract Review also appears here automatically.

### The Cross-Document Table

The table has one row per flagged clause with the columns Document, Clause, Risk, Category, Confidence, GDPR, DORA, and Page. Risk and confidence cells are colour-coded. Rows are sorted by severity. Two filters let you narrow the table by document and by risk level. The filtered table can be exported with **Download CSV**.

---

## Document Search

This view enables semantic search across multiple indexed contracts simultaneously.

### Indexing Contracts

1. Ensure your PDF contracts are in the `./sample_contracts` folder or change the folder path in the input field.
2. Click **Index all contracts**. The system reads each PDF, extracts clauses, generates vector embeddings using ChromaDB's built-in embedding model (all-MiniLM-L6-v2), and stores each clause with metadata in a local ChromaDB database.
3. The sidebar shows the list of indexed documents and the total number of clauses in the database.

### How RAG Works

When you submit a search query, the system converts it into a vector embedding, queries ChromaDB to find the most semantically similar clauses, and returns the top matches with similarity scores, filenames, and clause titles.

Example queries: `termination without notice`, `data breach notification`, `liability cap`, `automatic renewal`.

### Cross-Document Agent Chat

Below the search results, a chat interface allows questions that span all indexed documents. The agent uses the `search_contract` tool to retrieve relevant clauses from ChromaDB and synthesises answers across multiple documents.

---

## Regulatory Grounding

The system is grounded in the following regulatory frameworks, embedded directly in the model's system context:

**GDPR articles:** 28 (Processor obligations), 33 (Data breach notification), 46 (Transfers outside EEA), 82 (Right to compensation)

**DORA articles:** 19 (Reporting of major ICT incidents), 28 (ICT third-party risk), 30 (Key contractual provisions)

These article texts are included in the prompts so the model can cite specific requirements rather than relying on general knowledge.

---

## Limitations

**Clause segmentation** depends on numbered formatting conventions. Contracts with unusual or inconsistent structure may not be segmented correctly.

**Risk categories** were defined by the development team based on general legal knowledge, not by certified legal professionals. All outputs should be reviewed by a qualified legal professional.

**RAG does not include pre-computed risk analysis.** When contracts are indexed into ChromaDB, only the raw clause text is stored, not the risk analysis results. A full risk analysis is only available for the single contract uploaded in Contract Review. Performing a full analysis across all indexed documents simultaneously would require one LLM call per clause, which for larger document sets would mean significant latency and API usage.

**Language support** is limited to English.

**Groq rate limits.** The free tier of the Groq API has daily and per-minute request limits. Analysing a contract with 10 clauses requires 10 API calls.

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
├── .env.example            # API key template
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
