import fitz  # PyMuPDF
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


def read_multiple_pdfs(folder_path):
    """Read all PDFs from a folder and return list of documents"""
    documents = []

    for pdf_file in Path(folder_path).glob("*.pdf"):
        doc = fitz.open(pdf_file)

        # Extract text with page numbers
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()

            documents.append({
                "filename": pdf_file.name,
                "page": page_num,
                "text": text,
                "source": f"{pdf_file.name}, Page {page_num}"
            })

        doc.close()

    return documents


def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into chunks with metadata"""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for doc in documents:
        # Split text into chunks
        text_chunks = text_splitter.split_text(doc["text"])

        # Add metadata to each chunk
        for i, chunk_text in enumerate(text_chunks):
            chunks.append({
                "text": chunk_text,
                "filename": doc["filename"],
                "page": doc["page"],
                "chunk_id": f"{doc['filename']}_p{doc['page']}_c{i}",
                "source": doc["source"]
            })

    return chunks


# Test it
if __name__ == "__main__":
    # Use absolute path relative to project root
    import os
    project_root = Path(__file__).parent.parent
    contracts_path = project_root / "data" / "contracts"

    print(f"Looking for PDFs in: {contracts_path}")

    docs = read_multiple_pdfs(contracts_path)

    if len(docs) == 0:
        print("ERROR: No PDFs found!")
        print(f"Please add PDF files to: {contracts_path}")
    else:
        print(f"[OK] Loaded {len(docs)} pages from {len(set(d['filename'] for d in docs))} documents")
        print(f"\nFirst page preview:\n{docs[0]['text'][:200]}...")

        # Test chunking
        print("\n" + "="*60)
        print("Testing chunking...")
        chunks = chunk_documents(docs)

        print(f"[OK] Created {len(chunks)} chunks from {len(docs)} pages")
        print(f"\nFirst chunk:")
        print(f"  File: {chunks[0]['filename']}")
        print(f"  Page: {chunks[0]['page']}")
        print(f"  Chunk ID: {chunks[0]['chunk_id']}")
        print(f"  Text: {chunks[0]['text'][:150]}...")