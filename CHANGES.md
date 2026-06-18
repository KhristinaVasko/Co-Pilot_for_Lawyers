# CHANGES.md

## Feedback received at the poster session

### Feedback 1
Reviewer suggested better vector database indexing.

**Response:** Acknowledged. The current ChromaDB setup uses cosine similarity with
the all-MiniLM-L6-v2 embedding model which is appropriate for semantic clause search.
Further tuning is identified as future work.

---

### Feedback 2
Reviewer suggested improving poster readability.

**Response:** Poster layout and font sizing have been revised for the final submission.

---

### Feedback 3
Reviewer noted the system is too shallow and only works if the clause is explicitly
stated by name. Suggested recognizing clauses even if not explicitly named.

**Response:** This is a known limitation of our regex-based clause splitter which
relies on numbered headings (e.g. "1. Termination") or formal markers (ARTICLE, Section).
An LLM-based or semantic chunker would address this. Identified as future work due to
time constraints.

---

### Feedback 4
Reviewer suggested using an LLM agent chunker instead of regex, as regex is
result-based and not context-based.

**Response:** Agreed in principle. Regex clause splitting is a known limitation
documented in our README. LLM-based chunking is identified as future work.

---

### Feedback 5
Reviewer suggested thinking about precision of rewrites given legal exactness requirements,
and recommended testing with a boilerplate contract where clauses are removed to measure
legal exposure.

**Response:** The rewrite feature uses temperature=0.3 and always includes the full
rewritten clause with the original risk context. The suggested test scenario is a good
evaluation approach and will be considered for future validation.

---

### Feedback 6
Reviewer suggested the tool should be able to handle a large number of documents faster,
and recommended semantic chunking.

**Response:** Batch analysis across multiple documents is implemented in the Risk Overview
view. Speed limitations with large document sets are acknowledged as future work.
Semantic chunking was considered but not implemented within the project timeline.

---

### Feedback 7
Reviewer noted the referenced PDF page is not displayed in the UI.

**Response:** Page numbers are displayed in the Risk tab for every identified risk
("Source: page N") and in Document Search results. This feature was already implemented
and may not have been visible during the poster demo.

---

## What was implemented after the poster session

- Added Risk Overview view with cross-document risk table showing risk level, category,
  confidence, GDPR and DORA references across all analysed documents
- Risk analysis results are now persisted to disk (./risk_analysis/) so they survive
  session restarts
- Added CSV export for the cross-document risk table
- Added .env support for API key configuration
- Replaced hardcoded API key fallback with environment variable only
