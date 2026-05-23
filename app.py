import streamlit as st
import fitz
import json
import re
import os
import glob
from groq import Groq
import chromadb

st.set_page_config(
    page_title="Copilot for Lawyers",
    layout="wide",
    page_icon="⚖️",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Simple, readable Streamlit styling. Avoid global color overrides that break widgets. */
    :root {
        --bg: #F6F8FB;
        --card: #FFFFFF;
        --border: #D7DEE8;
        --text: #172033;
        --muted: #586579;
        --primary: #2952A3;
        --primary-soft: #EAF1FF;
        --high-bg: #FDECEC;
        --high-text: #8A1F1F;
        --medium-bg: #FFF4DB;
        --medium-text: #704400;
        --low-bg: #EAF3FF;
        --low-text: #164A7A;
        --safe-bg: #EAF7F0;
        --safe-text: #0B5A43;
    }

    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 1.25rem 1.5rem !important; max-width: 100% !important;}
    .stApp {background: var(--bg) !important;}

    /* Main text only, without forcing every nested widget element. */
    h1, h2, h3, h4, h5, h6, p, label, span, div[data-testid="stMarkdownContainer"] {
        color: var(--text) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: var(--text) !important;
    }
    [data-testid="stSidebar"] > div {padding: 0.75rem !important;}

    /* Inputs: readable, but do not overwrite uploader internals. */
    .stTextInput input,
    .stChatInput textarea {
        background: #FFFFFF !important;
        color: var(--text) !important;
        border: 1px solid #BFC8D6 !important;
        border-radius: 10px !important;
    }
    .stTextInput input::placeholder,
    .stChatInput textarea::placeholder {
        color: #758195 !important;
        opacity: 1 !important;
    }

    /* File uploader: keep button readable and separate from text. */
    [data-testid="stFileUploader"] section {
        background: #FFFFFF !important;
        border: 1px dashed #AEB9C8 !important;
        border-radius: 12px !important;
        padding: 18px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: var(--text) !important;
    }
    [data-testid="stFileUploader"] button {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--primary) !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton > button {
        background: #FFFFFF !important;
        color: var(--text) !important;
        border: 1px solid #BFC8D6 !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background: var(--primary-soft) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        border-color: var(--primary) !important;
    }
    .stButton > button[kind="primary"] * {color: #FFFFFF !important;}

    /* Metrics/cards */
    [data-testid="metric-container"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    [data-testid="stMetricLabel"] {color: var(--muted) !important; font-weight: 600 !important;}
    [data-testid="stMetricValue"] {color: var(--text) !important; font-weight: 700 !important;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 2px !important;
        padding: 0 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--muted) !important;
        background: transparent !important;
        border-radius: 8px 8px 0 0 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 10px 16px !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.15s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary) !important;
        background: var(--primary-soft) !important;
        border-radius: 8px 8px 0 0 !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        background: var(--primary-soft) !important;
        border-bottom: 2px solid var(--primary) !important;
        border-radius: 8px 8px 0 0 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
        background: transparent !important;
        height: 0 !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Chat and expanders */
    [data-testid="stChatMessage"], details {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatMessage"] * {color: var(--text) !important;}
    details > summary {
        background: white !important;
        color: var(--text) !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
    }
    details[open] > summary {
        border-radius: 12px 12px 0 0 !important;
    }
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {
        color: #888 !important;
    }

    /* Status boxes */
    .stSuccess {background: var(--safe-bg) !important; color: var(--safe-text) !important; border-radius: 10px !important;}
    .stSuccess * {color: var(--safe-text) !important;}
    .stError {background: var(--high-bg) !important; color: var(--high-text) !important; border-radius: 10px !important;}
    .stError * {color: var(--high-text) !important;}
    .stWarning {background: var(--medium-bg) !important; color: var(--medium-text) !important; border-radius: 10px !important;}
    .stWarning * {color: var(--medium-text) !important;}
    .stInfo {background: var(--low-bg) !important; color: var(--low-text) !important; border-radius: 10px !important;}
    .stInfo * {color: var(--low-text) !important;}

    hr {border-color: var(--border) !important; margin: 14px 0 !important;}
</style>
""", unsafe_allow_html=True)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR API")
CONTRACTS_FOLDER = "./sample_contracts"

client = Groq(api_key=GROQ_API_KEY)
chroma_client = chromadb.PersistentClient(path="./contract_db")
collection = chroma_client.get_or_create_collection(
    name="contract_chunks",
    metadata={"hnsw:space": "cosine"}
)

GDPR_DORA_CONTEXT = """
GDPR KEY ARTICLES:

Article 28 - Processor obligations:
A processor shall not engage another processor without prior specific or general written
authorisation of the controller. The processor shall implement appropriate technical and
organisational measures to ensure a level of security appropriate to the risk.

Article 33 - Notification of personal data breach:
In the case of a personal data breach, the controller shall notify the supervisory authority
without undue delay and, where feasible, not later than 72 hours after having become aware of it.
The processor must notify the controller without undue delay after becoming aware of a personal data breach.

Article 46 - Transfers subject to appropriate safeguards:
A controller or processor may transfer personal data to a third country only if appropriate safeguards are in place.

Article 82 - Right to compensation:
Any person who has suffered material or non-material damage as a result of an infringement
of this Regulation shall have the right to receive compensation.

DORA KEY ARTICLES:

Article 28 - ICT third-party risk:
Financial entities shall only enter into contractual arrangements with ICT third-party service
providers that comply with appropriate information security standards.

Article 30 - Key contractual provisions:
Contracts must include: clear description of all functions, data locations, availability,
integrity, security requirements, audit rights, termination rights, and incident reporting.

Article 19 - Reporting of major ICT incidents:
Financial entities shall report major ICT-related incidents to the competent authority.
"""

SYSTEM_PROMPT = """You are an expert contract lawyer. Analyze the given contract clause and identify any legal risks.

You must respond with a valid JSON object in exactly this format:
{
    "risk_level": "none" or "low" or "medium" or "high",
    "category": "short category name or null if no risk",
    "original_text": "exact quote of the risky part or null if no risk",
    "explanation": "short explanation of the risk or null if no risk",
    "gdpr_reference": "relevant GDPR article if applicable or null",
    "dora_reference": "relevant DORA article if applicable or null",
    "confidence": "found" or "uncertain" or "not_specified"
}

Risk categories to look for:
- Unilateral termination without notice
- Automatic renewal without notification
- Liability cap below contract value
- Unilateral fee increases
- Missing data breach notification (GDPR Article 33)
- Data transfer outside EEA without safeguards (GDPR Article 46)
- Unilateral contract amendment
- Excessive interest rates
- One-sided termination rights
- Missing audit rights (DORA Article 30)
- Missing incident reporting (DORA Article 19)

For the confidence field, use:
- "found" when a clear risk is identified with high certainty
- "uncertain" when there may be a risk but the clause wording is ambiguous
- "not_specified" when the clause does not address this area at all

Respond ONLY with the JSON object, no other text."""

def read_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        pages.append({"page_number": i + 1, "text": page.get_text()})
    doc.close()
    full_text = "\n".join(p["text"] for p in pages)
    return full_text, pages

def extract_clauses(text, pages=None):
    pattern = r'((?<!\d)([1-9]|1[0-9]|20)\.\s+[A-Z][^\n]+|(?:ARTICLE|Section|SCHEDULE)\s+[IVXLC\d]+[^\n]*)'
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    clauses = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        clause_text = text[start:end].strip()
        page_number = 1
        if pages:
            char_count = 0
            for p in pages:
                char_count += len(p["text"])
                if char_count >= start:
                    page_number = p["page_number"]
                    break
        clauses.append({"number": i+1, "title": match.group(0).strip(), "text": clause_text, "page_number": page_number})
    return clauses

def analyze_clause(clause_text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this clause:\n\n{clause_text}"}
            ],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        if not raw:
            return {"risk_level": "none", "category": None, "original_text": None, "explanation": None, "gdpr_reference": None, "dora_reference": None}
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        if "dora_reference" not in result:
            result["dora_reference"] = None
        if "confidence" not in result:
            result["confidence"] = "found" if result.get("risk_level") not in ["none", None] else "not_specified"
        return result
    except Exception as e:
        return {"risk_level": "none", "category": None, "original_text": None, "explanation": str(e), "gdpr_reference": None, "dora_reference": None}

def generate_highlighted_html(original_text, results):
    highlighted_text = original_text
    colors = {"high": "#FFEBEB", "medium": "#FFF4E0", "low": "#E8F0FF"}
    borders = {"high": "#E24B4A", "medium": "#EF9F27", "low": "#378ADD"}
    for r in sorted(results, key=lambda x: {"high": 0, "medium": 1, "low": 2, "none": 3}.get(x["risk_level"], 3)):
        if r["risk_level"] == "none" or not r.get("original_text"):
            continue
        risk_text = r["original_text"]
        color = colors.get(r["risk_level"], "#fff")
        border = borders.get(r["risk_level"], "#ccc")
        tooltip = f"{r.get('category', '')}: {r.get('explanation', '')}"
        highlighted = f'<mark style="background:{color}; border-bottom:2px solid {border}; padding:1px 0; cursor:help;" title="{tooltip}">{risk_text}</mark>'
        highlighted_text = highlighted_text.replace(risk_text, highlighted)
    return f'<div style="font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:white; border:0.5px solid #E8E6E0; border-radius:12px; padding:20px; line-height:1.8; font-size:13px; color:#333; white-space:pre-wrap; max-height:500px; overflow-y:auto;">{highlighted_text}</div>'

def index_contract(clauses, filename):
    existing = collection.get(where={"filename": filename})
    if existing["ids"]:
        collection.delete(where={"filename": filename})
    if not clauses:
        return
    documents, metadatas, ids = [], [], []
    for clause in clauses:
        documents.append(clause["text"])
        metadatas.append({"filename": filename, "clause_number": clause["number"], "clause_title": clause["title"], "page_number": clause.get("page_number", 1)})
        ids.append(f"{filename}_clause_{clause['number']}")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

def retrieve_relevant_clauses(query, n_results=5):
    total = collection.count()
    if total == 0:
        return []
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, total),
        include=["documents", "metadatas", "distances"]
    )
    return [{
        "clause_title": results["metadatas"][0][i]["clause_title"],
        "clause_number": results["metadatas"][0][i]["clause_number"],
        "filename": results["metadatas"][0][i]["filename"],
        "page_number": results["metadatas"][0][i].get("page_number", 1),
        "text": results["documents"][0][i],
        "similarity_score": round(1 - results["distances"][0][i], 3)
    } for i in range(len(results["ids"][0]))]

def index_all_contracts(folder_path):
    pdf_files = glob.glob(f"{folder_path}/*.pdf")
    if not pdf_files:
        return 0, []
    log = []
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        try:
            contract_text, contract_pages = read_pdf(pdf_path)
            contract_clauses = extract_clauses(contract_text, contract_pages)
            index_contract(contract_clauses, filename)
            log.append((filename, len(contract_clauses), None))
        except Exception as e:
            log.append((filename, 0, str(e)))
    return len(pdf_files), log

def get_clause_by_number(clause_number, clauses):
    for c in clauses:
        if c["number"] == clause_number:
            return c["text"]
    return "Clause not found"

def get_risk_for_clause(clause_number, results):
    for r in results:
        if r.get("clause_number") == clause_number:
            return r
    return {"explanation": "No risk data found"}

def rewrite_clause_fn(clause_number, clauses, results):
    clause_text = get_clause_by_number(clause_number, clauses)
    risk = get_risk_for_clause(clause_number, results)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a legal expert. Rewrite the following clause to be safer and more balanced for both parties. Always include the full rewritten clause."},
            {"role": "user", "content": f"Clause {clause_number}:\n\n{clause_text}\n\nRisk: {risk.get('explanation', 'General risk')}\n\nProvide a safer rewrite."}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def get_regulatory_analysis_fn(clause_number, clauses):
    clause_text = get_clause_by_number(clause_number, clauses)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are a legal expert specializing in GDPR and DORA. Analyze the clause and cite specific articles.\n\n{GDPR_DORA_CONTEXT}"},
            {"role": "user", "content": f"Analyze this clause for GDPR and DORA compliance:\n\n{clause_text}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

def summarize_all_risks_fn(results):
    high = [r for r in results if r["risk_level"] == "high"]
    medium = [r for r in results if r["risk_level"] == "medium"]
    low = [r for r in results if r["risk_level"] == "low"]
    summary = f"Total risks: {len(high) + len(medium) + len(low)}\nHigh: {len(high)}, Medium: {len(medium)}, Low: {len(low)}\n\n"
    for r in high + medium + low:
        summary += f"[{r['risk_level'].upper()}] {r.get('clause_title', '')}: {r.get('explanation', '')}\n"
    return summary

def search_contract_fn(query):
    retrieved = retrieve_relevant_clauses(query, n_results=5)
    if not retrieved:
        return "No relevant clauses found."
    return "\n\n".join([f"[Score: {r['similarity_score']}] {r['filename']} — {r['clause_title']}\n{r['text']}" for r in retrieved])

TOOLS_SCHEMA = [
    {"type": "function", "function": {"name": "get_clause_by_number", "description": "Get the full text of a specific clause by its number", "parameters": {"type": "object", "properties": {"clause_number": {"type": "integer"}}, "required": ["clause_number"]}}},
    {"type": "function", "function": {"name": "rewrite_clause", "description": "Rewrite a risky clause to be safer and more balanced", "parameters": {"type": "object", "properties": {"clause_number": {"type": "integer"}}, "required": ["clause_number"]}}},
    {"type": "function", "function": {"name": "get_regulatory_analysis", "description": "Analyze a clause for GDPR and DORA compliance with specific article references", "parameters": {"type": "object", "properties": {"clause_number": {"type": "integer"}}, "required": ["clause_number"]}}},
    {"type": "function", "function": {"name": "summarize_all_risks", "description": "Get a complete summary of all risks found in the contract", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "search_contract", "description": "Semantically search contract clauses by meaning across all indexed documents", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}
]

def run_agent(user_message, clauses, results):
    messages = [
        {"role": "system", "content": f"You are a legal assistant for contract review. Use the available tools to answer questions.\n\n{GDPR_DORA_CONTEXT}"},
        {"role": "user", "content": user_message}
    ]
    tool_map = {
        "get_clause_by_number": lambda clause_number: get_clause_by_number(clause_number, clauses),
        "rewrite_clause": lambda clause_number: rewrite_clause_fn(clause_number, clauses, results),
        "get_regulatory_analysis": lambda clause_number: get_regulatory_analysis_fn(clause_number, clauses),
        "summarize_all_risks": lambda **kw: summarize_all_risks_fn(results),
        "search_contract": lambda query=None, **kw: search_contract_fn(query or ""),
    }
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto",
        temperature=0.1
    )
    message = response.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        try:
            tool_result = tool_map[tool_name](**tool_args)
        except Exception:
            tool_result = "Tool call failed."
        messages.append(message)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})
        final = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, temperature=0.3)
        return final.choices[0].message.content, tool_name
    return message.content, None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 16px 12px; border-bottom:0.5px solid #E8E6E0; margin-bottom:8px;">
        <p style="font-size:15px; font-weight:500; color:#111 !important; margin:0;">⚖️ Copilot for Lawyers</p>
        <p style="font-size:12px; color:#888 !important; margin:4px 0 0;">AI contract review</p>
    </div>
    """, unsafe_allow_html=True)

    view = st.radio("Navigation", ["Contract Review", "Document Search"], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#E8E6E0; margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.05em; padding:0 4px; margin-bottom:4px;">Indexed documents</p>', unsafe_allow_html=True)

    total_docs = collection.count()
    if total_docs > 0:
        try:
            all_meta = collection.get(include=["metadatas"])
            filenames = list(set(m["filename"] for m in all_meta["metadatas"]))
            for fname in filenames[:8]:
                st.markdown(f'<div style="font-size:12px; color:#555 !important; padding:3px 4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">📄 {fname}</div>', unsafe_allow_html=True)
        except:
            pass
    else:
        st.markdown('<div style="font-size:12px; color:#aaa; padding:4px;">No documents indexed yet</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:11px; color:#aaa; padding:4px; margin-top:4px;">{total_docs} clauses indexed</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1: CONTRACT REVIEW
# ══════════════════════════════════════════════════════════════════════════════
if view == "Contract Review":
    uploaded_file = st.file_uploader("Upload a contract (PDF)", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        with st.spinner("Reading contract..."):
            with open("temp_contract.pdf", "wb") as f:
                f.write(uploaded_file.getvalue())
            text, pages = read_pdf("temp_contract.pdf")
            clauses = extract_clauses(text, pages)

        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.markdown(f'<p style="font-size:13px; color:#555; margin:8px 0;">📄 <strong>{uploaded_file.name}</strong> — {len(clauses)} clauses detected</p>', unsafe_allow_html=True)
        with col_btn:
            analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

        if analyze_clicked:
            analysis_results = []
            progress = st.progress(0, text="Analyzing clauses...")
            for i, clause in enumerate(clauses):
                result = analyze_clause(clause["text"])
                result["clause_title"] = clause["title"]
                result["clause_number"] = clause["number"]
                analysis_results.append(result)
                progress.progress((i + 1) / len(clauses), text=f"Analyzing: {clause['title']}...")
            progress.empty()
            st.session_state["results"] = analysis_results
            st.session_state["text"] = text
            st.session_state["clauses"] = clauses
            st.session_state["filename"] = uploaded_file.name
            st.session_state["chat_history"] = []
            st.session_state.pop("selected_clause", None)
            index_contract(clauses, uploaded_file.name)
            st.rerun()

    if "results" in st.session_state:
        results = st.session_state["results"]
        text = st.session_state["text"]
        clauses = st.session_state["clauses"]

        risks = [r for r in results if r["risk_level"] != "none"]
        high_risks = [r for r in results if r["risk_level"] == "high"]
        medium_risks = [r for r in results if r["risk_level"] == "medium"]
        low_risks = [r for r in results if r["risk_level"] == "low"]
        gdpr_violations = [r for r in results if r.get("gdpr_reference")]
        dora_violations = [r for r in results if r.get("dora_reference")]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total risks", len(risks))
        c2.metric("High risk", len(high_risks))
        c3.metric("Medium risk", len(medium_risks))
        c4.metric("GDPR violations", len(gdpr_violations))
        c5.metric("DORA violations", len(dora_violations))

        st.markdown("<hr style='border-color:#E8E6E0; margin:16px 0;'>", unsafe_allow_html=True)

        col_clauses, col_detail = st.columns([1, 1])

        with col_clauses:
            st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">Clauses</p>', unsafe_allow_html=True)

            for r in results:
                border_color = {"high": "#E24B4A", "medium": "#EF9F27", "low": "#378ADD", "none": "#E8E6E0"}.get(r["risk_level"], "#E8E6E0")
                risk_bg = {"high": "#FFEBEB", "medium": "#FFF4E0", "low": "#E8F0FF", "none": "transparent"}.get(r["risk_level"], "transparent")
                risk_label = {"high": "HIGH", "medium": "MED", "low": "LOW"}.get(r["risk_level"], "")
                badge_color = {"high": "#A32D2D", "medium": "#854F0B", "low": "#185FA5"}.get(r["risk_level"], "#888")
                gdpr_badge = '<span style="font-size:10px; background:#EEEDFE; color:#534AB7; padding:1px 6px; border-radius:999px; margin-left:4px;">GDPR</span>' if r.get("gdpr_reference") else ""
                dora_badge = '<span style="font-size:10px; background:#E1F5EE; color:#0F6E56; padding:1px 6px; border-radius:999px; margin-left:4px;">DORA</span>' if r.get("dora_reference") else ""
                risk_badge = f'<span style="font-size:10px; font-weight:500; color:{badge_color}; background:{risk_bg}; padding:2px 6px; border-radius:999px;">{risk_label}</span>' if risk_label else ""
                explanation_preview = f'<div style="font-size:11px; color:#888; line-height:1.4; margin-top:3px;">{r.get("explanation", "")[:80]}...</div>' if r.get("explanation") else ""

                st.markdown(f"""
                <div style="background:white; border-left:3px solid {border_color}; border-radius:0 8px 8px 0; border:0.5px solid #E8E6E0; border-left:3px solid {border_color}; padding:10px 12px; margin-bottom:6px;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:2px;">
                        <span style="font-size:12px; font-weight:500; color:#111;">{r['clause_title']}</span>
                        <div style="display:flex; align-items:center; gap:4px; flex-shrink:0;">{gdpr_badge}{dora_badge}{risk_badge}</div>
                    </div>
                    {explanation_preview}
                </div>
                """, unsafe_allow_html=True)

                if r["risk_level"] != "none":
                    if st.button("Details →", key=f"sel_{r['clause_number']}"):
                        st.session_state["selected_clause"] = r["clause_number"]
                        st.rerun()

        with col_detail:
            selected_num = st.session_state.get("selected_clause")
            if selected_num:
                sel = next((r for r in results if r["clause_number"] == selected_num), None)
                if sel:
                    risk_bg = {"high": "#FFEBEB", "medium": "#FFF4E0", "low": "#E8F0FF"}.get(sel["risk_level"], "#F8F7F4")
                    border_color = {"high": "#E24B4A", "medium": "#EF9F27", "low": "#378ADD"}.get(sel["risk_level"], "#E8E6E0")

                    st.markdown(f'<p style="font-size:13px; font-weight:500; color:#111; margin-bottom:8px;">{sel["clause_title"]}</p>', unsafe_allow_html=True)

                    tab_risk, tab_gdpr, tab_rewrite, tab_chat = st.tabs(["Risk", "GDPR / DORA", "Rewrite", "Agent chat"])

                    with tab_risk:
                        if sel.get("category"):
                            st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Category</p>', unsafe_allow_html=True)
                            st.markdown(f'<p style="font-size:13px; color:#333; margin-bottom:12px;">{sel["category"]}</p>', unsafe_allow_html=True)
                        if sel.get("original_text"):
                            st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">Risky excerpt</p>', unsafe_allow_html=True)
                            st.markdown(f'<div style="background:{risk_bg}; border-left:3px solid {border_color}; padding:8px 12px; border-radius:0 8px 8px 0; font-size:12px; color:#333; line-height:1.6; margin-bottom:12px;">{sel["original_text"]}</div>', unsafe_allow_html=True)
                        if sel.get("explanation"):
                            st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">Explanation</p>', unsafe_allow_html=True)
                            st.markdown(f'<p style="font-size:13px; color:#333; line-height:1.6;">{sel["explanation"]}</p>', unsafe_allow_html=True)
                        if sel.get("confidence"):
                            conf = sel["confidence"]
                            conf_color = {"found": "#0B5A43", "uncertain": "#704400", "not_specified": "#586579"}.get(conf, "#586579")
                            conf_bg = {"found": "#EAF7F0", "uncertain": "#FFF4DB", "not_specified": "#F0F2F5"}.get(conf, "#F0F2F5")
                            conf_label = {"found": "Confirmed risk", "uncertain": "Uncertain — review manually", "not_specified": "Not specified in clause"}.get(conf, conf)
                            st.markdown(f'<div style="margin-top:12px; display:inline-block; background:{conf_bg}; color:{conf_color}; font-size:11px; font-weight:600; padding:4px 10px; border-radius:999px;">⬤ {conf_label}</div>', unsafe_allow_html=True)
                        page_num = sel.get("page_number", 1)
                        st.markdown(f'<p style="font-size:11px; color:#aaa; margin-top:8px;">📄 Source: page {page_num}</p>', unsafe_allow_html=True)

                    with tab_gdpr:
                        if sel.get("gdpr_reference"):
                            st.markdown(f'<div style="background:#FCEBEB; border-radius:8px; padding:12px 14px; margin-bottom:8px;"><div style="font-size:12px; font-weight:500; color:#7A1F1F; margin-bottom:4px;">GDPR — {sel["gdpr_reference"]}</div><div style="font-size:12px; color:#501313; line-height:1.5;">This clause may violate {sel["gdpr_reference"]}.</div></div>', unsafe_allow_html=True)
                        if sel.get("dora_reference"):
                            st.markdown(f'<div style="background:#E1F5EE; border-radius:8px; padding:12px 14px; margin-bottom:8px;"><div style="font-size:12px; font-weight:500; color:#085041; margin-bottom:4px;">DORA — {sel["dora_reference"]}</div><div style="font-size:12px; color:#04342C; line-height:1.5;">This clause may violate {sel["dora_reference"]}.</div></div>', unsafe_allow_html=True)
                        if not sel.get("gdpr_reference") and not sel.get("dora_reference"):
                            st.markdown('<p style="font-size:13px; color:#888;">No GDPR or DORA violations detected for this clause.</p>', unsafe_allow_html=True)
                        st.markdown("<hr style='border-color:#E8E6E0;'>", unsafe_allow_html=True)
                        if st.button("Run full GDPR/DORA analysis", key=f"reg_{selected_num}"):
                            with st.spinner("Analyzing..."):
                                reg = get_regulatory_analysis_fn(selected_num, clauses)
                            st.markdown(reg)

                    with tab_rewrite:
                        st.markdown('<p style="font-size:12px; color:#888; margin-bottom:12px;">Generate a safer, more balanced version of this clause.</p>', unsafe_allow_html=True)
                        if st.button("Generate rewrite", key=f"rewrite_btn_{selected_num}", type="primary"):
                            with st.spinner("Rewriting..."):
                                rewritten = rewrite_clause_fn(selected_num, clauses, results)
                            st.session_state[f"rewrite_{selected_num}"] = rewritten
                        if st.session_state.get(f"rewrite_{selected_num}"):
                            st.markdown(f'<div style="background:#E1F5EE; border-left:3px solid #1D9E75; border-radius:0 8px 8px 0; padding:12px 14px; font-size:12px; line-height:1.7; color:#04342C; margin-top:8px;">{st.session_state[f"rewrite_{selected_num}"]}</div>', unsafe_allow_html=True)

                    with tab_chat:
                        chat_key = f"chat_clause_{selected_num}"
                        if chat_key not in st.session_state:
                            st.session_state[chat_key] = []
                        for msg in st.session_state[chat_key]:
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])
                                if msg.get("tool_used"):
                                    st.caption(f"Tool used: `{msg['tool_used']}`")
                        if prompt := st.chat_input("Ask about this contract...", key="chat_main"):
                            st.session_state[chat_key].append({"role": "user", "content": prompt})
                            with st.chat_message("user"):
                                st.markdown(prompt)
                            with st.chat_message("assistant"):
                                with st.spinner("Thinking..."):
                                    clause_context = f"The user is currently viewing clause {selected_num}: '{sel['clause_title']}'. Risk level: {sel.get('risk_level', 'unknown')}. When the user says 'this clause' or 'rewrite this' they mean clause {selected_num}."
                                    augmented_prompt = f"{clause_context}\n\nUser question: {prompt}"
                                    response, tool_used = run_agent(augmented_prompt, clauses, results)
                                st.markdown(response)
                                if tool_used:
                                    st.caption(f"Tool used: `{tool_used}`")
                            st.session_state[chat_key].append({"role": "assistant", "content": response, "tool_used": tool_used})
            else:
                st.markdown('<div style="background:white; border:0.5px solid #E8E6E0; border-radius:12px; padding:48px; text-align:center; margin-top:16px;"><div style="font-size:32px; margin-bottom:8px;">👈</div><div style="font-size:13px; color:#888;">Select a clause to view details</div></div>', unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#E8E6E0; margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">Highlighted contract</p>', unsafe_allow_html=True)
        st.components.v1.html(generate_highlighted_html(text, results), height=500, scrolling=True)

    elif not uploaded_file:
        st.markdown('<div style="background:white; border:1.5px dashed #D0CEC8; border-radius:12px; padding:48px; text-align:center; margin-top:16px;"><div style="font-size:40px; margin-bottom:12px;">📄</div><div style="font-size:14px; color:#888; margin-bottom:4px;">Upload a contract to get started</div><div style="font-size:12px; color:#bbb;">Supports PDF files</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2: DOCUMENT SEARCH
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<p style="font-size:18px; font-weight:500; color:#111; margin-bottom:4px;">Document search</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px; color:#888; margin-bottom:16px;">Search semantically across all indexed contracts</p>', unsafe_allow_html=True)

    col_f, col_b = st.columns([3, 1])
    with col_f:
        folder_path = st.text_input("Folder", value=CONTRACTS_FOLDER, label_visibility="collapsed")
    with col_b:
        if st.button("Index all contracts", type="primary", use_container_width=True):
            with st.spinner("Indexing..."):
                n_files, log = index_all_contracts(folder_path)
            if n_files == 0:
                st.error("No PDF files found.")
            else:
                for fname, n_clauses, err in log:
                    if err:
                        st.warning(f"Error — {fname}: {err}")
                    else:
                        st.success(f"Indexed {fname} ({n_clauses} clauses)")
                st.info(f"Total clauses in database: {collection.count()}")
                st.rerun()

    st.markdown("<hr style='border-color:#E8E6E0; margin:12px 0;'>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.metric("Clauses indexed", collection.count())

    search_query = st.text_input("Search", placeholder="e.g. termination without notice, data breach, liability cap...", label_visibility="collapsed")
    n_results = st.slider("Number of results", 3, 15, 5, label_visibility="collapsed")

    if search_query:
        if collection.count() == 0:
            st.warning("No contracts indexed yet. Use the button above to index contracts first.")
        else:
            with st.spinner("Searching..."):
                search_results = retrieve_relevant_clauses(search_query, n_results=n_results)
            st.markdown(f'<p style="font-size:13px; color:#888; margin-bottom:8px;">Results for: <strong style="color:#111;">{search_query}</strong></p>', unsafe_allow_html=True)
            if not search_results:
                st.info("No results found.")
            else:
                for r in search_results:
                    score = r["similarity_score"]
                    sc = "#1D9E75" if score > 0.6 else "#EF9F27" if score > 0.4 else "#E24B4A"
                    sb = "#E1F5EE" if score > 0.6 else "#FFF4E0" if score > 0.4 else "#FFEBEB"
                    with st.expander(f"**{r['filename']}** — {r['clause_title']} (p. {r.get('page_number', '?')})" ):
                        st.markdown(f'<span style="font-size:11px; background:{sb}; color:{sc}; padding:2px 8px; border-radius:999px; font-weight:500;">Score: {score}</span> <span style="font-size:11px; color:#888; margin-left:8px;">Page {r.get("page_number", "?")}</span>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size:13px; color:#333; line-height:1.6; margin-top:8px;">{r["text"]}</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#E8E6E0; margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">Ask across all documents</p>', unsafe_allow_html=True)

    if "search_chat_history" not in st.session_state:
        st.session_state["search_chat_history"] = []

    for msg in st.session_state["search_chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_used"):
                st.caption(f"Tool used: `{msg['tool_used']}`")

    if prompt := st.chat_input("Ask anything across all indexed contracts...", key="search_chat"):
        st.session_state["search_chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                response, tool_used = run_agent(
                    prompt,
                    st.session_state.get("clauses", []),
                    st.session_state.get("results", [])
                )
            st.markdown(response)
            if tool_used:
                st.caption(f"Tool used: `{tool_used}`")
        st.session_state["search_chat_history"].append({"role": "assistant", "content": response, "tool_used": tool_used})
