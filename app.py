"""
Co-Pilot for Lawyers - Streamlit App
Main application for legal document analysis

STATUS: 🚧 UI SKELETON COMPLETE - Backend connections in progress

COMPLETED:
✅ Streamlit UI structure with 3 tabs
✅ File upload interface
✅ Mock data and placeholders

IN PROGRESS (3 connection points):
⏳ TODO #1: Extraction Engine (Line ~78) - Extract fields across documents
⏳ TODO #2: Rule Review Engine (Line ~150) - Check GDPR/DORA compliance
⏳ TODO #3: RAG Q&A Engine (Line ~210) - Answer questions with citations

NEXT STEPS:
1. Finish RAG foundation: src/vector_store.py
2. Create backend engines: extraction_engine.py, rule_engine.py, qa_engine.py
3. Replace TODO sections with real function calls
4. Test with real documents

SEE DETAILED COMMENTS AT EACH TODO SECTION FOR:
- Function signatures
- Expected input/output
- Files to create
- Implementation notes
"""

import streamlit as st

# ============================================================================
# FUTURE IMPORTS - Uncomment when backend is ready
# ============================================================================
# from src.vector_store import VectorStore
# from src.extraction_engine import extract_fields
# from src.rule_engine import check_compliance
# from src.qa_engine import ask_question
# from src.document_processor import read_multiple_pdfs, chunk_documents
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="Co-Pilot for Lawyers",
    page_icon="",
    layout="wide"
)

# Title and description
st.title("Co-Pilot for Lawyers")
st.markdown("AI-powered legal document analysis with source citations")

# Sidebar for document upload
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF contracts",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more legal contracts for analysis"
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} document(s) uploaded")

        # Show uploaded files
        with st.expander("View uploaded files"):
            for file in uploaded_files:
                st.write(f"- {file.name}")

    st.divider()

    # Settings (will be passed to backend engines)
    st.subheader("Settings")
    llm_model = st.selectbox("LLM Model", ["llama-3.3-70b-versatile", "gpt-4"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1)

    # TODO: Pass these settings to extraction_engine, rule_engine, qa_engine
    # Example: extract_fields(..., model=llm_model, temperature=temperature)

# Main content - Three tabs for three core features
tab1, tab2, tab3 = st.tabs(["Extraction", "Rule Review", "Q&A"])

# ============================================================================
# TAB 1: EXTRACTION
# ============================================================================
with tab1:
    st.header("Structured Extraction")
    st.markdown("Extract specific information from all uploaded contracts")

    # Field selection
    st.subheader("Select Fields to Extract")

    col1, col2 = st.columns(2)

    with col1:
        extract_governing_law = st.checkbox("Governing Law", value=True)
        extract_notice_period = st.checkbox("Notice Period", value=True)
        extract_liability_cap = st.checkbox("Liability Cap", value=True)

    with col2:
        extract_termination = st.checkbox("Termination Rights")
        extract_data_processing = st.checkbox("Data Processing Terms")
        extract_custom = st.checkbox("Custom Field")

    if extract_custom:
        custom_field = st.text_input("Enter custom field name:")

    # Extract button
    if st.button(" Run Extraction", type="primary"):
        if not uploaded_files:
            st.warning("Please upload documents first!")
        else:
            with st.spinner("Extracting information from documents..."):
                # ================================================================
                # TODO #1: CONNECT EXTRACTION ENGINE
                # ================================================================
                # What to do:
                #   1. Import: from src.extraction_engine import extract_fields
                #   2. Process uploaded files through RAG
                #   3. Extract selected fields from all documents
                #
                # Expected function signature:
                #   extract_fields(uploaded_files, field_list) -> DataFrame
                #
                # Input:
                #   - uploaded_files: list of Streamlit UploadedFile objects
                #   - field_list: ["governing_law", "notice_period", "liability_cap", ...]
                #
                # Output: pandas DataFrame with columns:
                #   - Document (filename)
                #   - One column per selected field
                #   - Each cell contains: {
                #       "value": extracted value or "Not Found" or "Not Specified",
                #       "confidence": "found" | "absent" | "uncertain",
                #       "citation": "contract.pdf, Page X, Clause Y",
                #       "passage": "exact text excerpt"
                #     }
                #
                # Files to create:
                #   - src/extraction_engine.py (extract from Jupyter notebook)
                #   - Connect to src/vector_store.py for RAG retrieval
                # ================================================================

                st.info("Extraction engine coming soon! (Will be connected after RAG is done)")

                # Placeholder table
                st.subheader("Extraction Results")
                st.markdown("*This is a preview - real data will appear here after RAG implementation*")

                import pandas as pd

                # Mock data for demonstration
                mock_data = {
                    "Document": ["contract1.pdf", "contract2.pdf"],
                    "Governing Law": ["Austria", "Germany"],
                    "Notice Period": ["30 days", "60 days"],
                    "Liability Cap": ["€500", "€1000"]
                }

                df = pd.DataFrame(mock_data)
                st.dataframe(df, use_container_width=True)

                st.info(" Click on cells to view source passages (coming soon)")

# ============================================================================
# TAB 2: RULE REVIEW
# ============================================================================
with tab2:
    st.header("Rule-Based Review")
    st.markdown("Check contracts against compliance rules and playbooks")

    # Rule selection
    st.subheader("Select Compliance Rules")

    col1, col2 = st.columns(2)

    with col1:
        check_gdpr = st.checkbox("GDPR Compliance", value=True)
        check_dora = st.checkbox("DORA Requirements", value=True)

    with col2:
        check_custom = st.checkbox("Custom Playbook")

        if check_custom:
            uploaded_playbook = st.file_uploader("Upload playbook (YAML)", type=['yaml', 'yml'])

    # Review button
    if st.button("Run Compliance Check", type="primary"):
        if not uploaded_files:
            st.warning(" Please upload documents first!")
        else:
            with st.spinner("Checking compliance..."):
                # ================================================================
                # TODO #2: CONNECT RULE-BASED REVIEW ENGINE
                # ================================================================
                # What to do:
                #   1. Import: from src.rule_engine import check_compliance
                #   2. Load selected rules (GDPR, DORA, custom playbook)
                #   3. Check each document against rules
                #   4. Return violations with exact citations
                #
                # Expected function signature:
                #   check_compliance(uploaded_files, rules) -> List[Violation]
                #
                # Input:
                #   - uploaded_files: list of Streamlit UploadedFile objects
                #   - rules: {
                #       "gdpr": True/False,
                #       "dora": True/False,
                #       "custom_playbook": file path or None
                #     }
                #
                # Output: List of violation objects with:
                #   {
                #     "severity": "high" | "medium" | "low",
                #     "rule_name": "Data Breach Notification",
                #     "document": "contract1.pdf",
                #     "location": "Clause 3, Page 1",
                #     "issue": "Missing 72-hour notification requirement",
                #     "regulation": "GDPR Article 33",
                #     "passage": "exact problematic text",
                #     "recommendation": "suggested fix"
                #   }
                #
                # Files to create:
                #   - src/rule_engine.py (refactor from Jupyter Cell 14+)
                #   - rules/gdpr_rules.yaml (predefined GDPR rules)
                #   - rules/dora_rules.yaml (predefined DORA rules)
                #   - Reuse existing GDPR_DORA_CONTEXT from notebook
                # ================================================================

                st.info("Rule engine coming soon! (Will be connected after RAG is done)")

                # Placeholder results
                st.subheader("Compliance Issues Found")
                st.markdown("*This is a preview - real violations will appear here after implementation*")

                # Mock violations
                with st.expander("🔴 HIGH - Data Breach Notification Missing", expanded=True):
                    st.markdown("**Document:** contract1.pdf")
                    st.markdown("**Location:** Clause 3, Page 1")
                    st.markdown("**Issue:** Contract does not require data breach notification within 72 hours")
                    st.markdown("**GDPR Reference:** Article 33")
                    st.code("The Service Provider shall not be required to notify the Client in the event of a personal data breach.")

                with st.expander("🟡 MEDIUM - Unilateral Termination"):
                    st.markdown("**Document:** contract2.pdf")
                    st.markdown("**Location:** Clause 7, Page 2")
                    st.markdown("**Issue:** Service provider can terminate without cause")
                    st.code("The Service Provider may terminate this Agreement at any time...")

# ============================================================================
# TAB 3: Q&A
# ============================================================================
with tab3:
    st.header("Research & Q&A")
    st.markdown("Ask questions across all uploaded documents")

    # Question input
    st.subheader("Ask a Question")

    # Example questions
    with st.expander("Example questions"):
        st.markdown("""
        - What are the notice periods in each contract?
        - Which contracts allow unilateral termination?
        - What are the liability caps?
        - Which contracts have GDPR violations?
        - What are the governing laws?
        """)

    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., Which contracts allow termination without cause?"
    )

    # Ask button
    if st.button(" Search", type="primary"):
        if not uploaded_files:
            st.warning(" Please upload documents first!")
        elif not question:
            st.warning(" Please enter a question!")
        else:
            with st.spinner("Searching documents..."):
                # ================================================================
                # TODO #3: CONNECT RAG Q&A ENGINE
                # ================================================================
                # What to do:
                #   1. Import: from src.qa_engine import ask_question
                #   2. Search vector database for relevant chunks
                #   3. Retrieve top-k most similar passages
                #   4. Send to LLM with context
                #   5. Generate answer with precise citations
                #
                # Expected function signature:
                #   ask_question(question, uploaded_files, vector_store) -> Answer
                #
                # Input:
                #   - question: string (user's question)
                #   - uploaded_files: list of Streamlit UploadedFile objects
                #   - vector_store: VectorStore instance (from src/vector_store.py)
                #
                # Output: Answer object with:
                #   {
                #     "answer": "synthesized answer text",
                #     "sources": [
                #       {
                #         "document": "contract1.pdf",
                #         "page": 2,
                #         "location": "Clause 7, Page 2",
                #         "passage": "exact text excerpt (150 chars)",
                #         "relevance_score": 0.95
                #       },
                #       ...
                #     ],
                #     "confidence": "high" | "medium" | "low",
                #     "found_in_documents": ["contract1.pdf", "contract2.pdf"]
                #   }
                #
                # Implementation notes:
                #   - Use ChromaDB similarity search (vector_store.search())
                #   - Retrieve top 3-5 most relevant chunks
                #   - Pass to Groq LLM with prompt engineering
                #   - Format citations as: "contract.pdf, Clause X, Page Y"
                #   - Handle "not found" cases gracefully
                #
                # Files to create:
                #   - src/qa_engine.py (new RAG Q&A implementation)
                #   - Connects: vector_store.py + Groq LLM
                # ================================================================

                st.info("RAG Q&A engine coming soon! (Will be connected after implementation)")

                # Placeholder answer
                st.subheader("Answer")
                st.markdown("*This is a preview - real answers will appear here after RAG implementation*")

                st.markdown("""
                Based on the uploaded documents, three contracts allow termination without cause:

                1. **contract1.pdf** - The Service Provider may terminate at any time
                   - Source: Clause 7, Page 2

                2. **contract2.pdf** - Either party with 90 days notice
                   - Source: Clause 8, Page 3

                3. **contract3.pdf** - Only Service Provider can terminate without cause
                   - Source: Clause 6, Page 2
                """)

                with st.expander("View Source Passages"):
                    st.code("The Service Provider may terminate this Agreement at any time and for any reason by providing written notice to the Client.")
                    st.caption("Source: contract1.pdf, Clause 7, Page 2")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.caption("Co-Pilot for Lawyers | TU Wien 2026 | Powered by RAG + LLMs")

# ============================================================================
# DEVELOPMENT ROADMAP - Connection Steps
# ============================================================================
# STEP 1 [IN PROGRESS]: Complete RAG Foundation
#   - Finish: src/vector_store.py (ChromaDB + embeddings)
#   - Test: Multi-document ingestion and search
#
# STEP 2: Create Backend Engines
#   - Create: src/extraction_engine.py (field extraction logic)
#   - Create: src/rule_engine.py (GDPR/DORA compliance checking)
#   - Create: src/qa_engine.py (RAG-based question answering)
#   - Refactor: Extract code from GenAI.ipynb into these files
#
# STEP 3: Connect to Streamlit
#   - Uncomment imports at top of this file
#   - Replace TODO #1 with: extract_fields(uploaded_files, ...)
#   - Replace TODO #2 with: check_compliance(uploaded_files, ...)
#   - Replace TODO #3 with: ask_question(question, ...)
#   - Remove mock data, display real results
#
# STEP 4: Testing & Polish
#   - Test with 10-20 real contracts
#   - Add error handling
#   - Improve UI/UX based on testing
#   - Add export functionality (CSV, Excel)
#
# STEP 5: Documentation
#   - Update README.md with screenshots
#   - Create demo video
#   - Prepare poster for presentation
# ============================================================================
