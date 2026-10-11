
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi


# Resolve the project directory independently of the terminal's location
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Actual folder name in your project: Documents (capital D)
DOCUMENTS_DIR = PROJECT_DIR / "Documents"


def load_documents():
    """Load PDF files and split their text into searchable chunks."""

    all_chunks = []

    if not DOCUMENTS_DIR.is_dir():
        raise FileNotFoundError(
            f"Documents folder not found: {DOCUMENTS_DIR}"
        )

    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    print("Documents folder:", DOCUMENTS_DIR)
    print("Total PDF files:", len(pdf_files))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")

        try:
            reader = PdfReader(str(pdf_file))
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            text = "\n".join(text_parts).strip()

            if not text:
                print("Warning: No extractable text found.")
                continue

            chunks = splitter.split_text(text)

            for chunk in chunks:
                all_chunks.append({
                    "text": chunk,
                    "source": pdf_file.name
                })

            print("Chunks created:", len(chunks))

        except Exception as exc:
            print(f"Warning: Could not process {pdf_file.name}: {exc}")

    return all_chunks


# Build the keyword search index
documents = load_documents()

texts = [item["text"] for item in documents]
sources = [item["source"] for item in documents]

bm25_index = None

if texts:
    tokenized_documents = [
        text.lower().split()
        for text in texts
    ]
    bm25_index = BM25Okapi(tokenized_documents)

print("Total searchable chunks:", len(texts))


def retrieve_documents(question, top_k=3):
    """Return BM25 results in the format expected by the existing RAG tools."""

    if bm25_index is None or not question.strip():
        return {
            "documents": [[]],
            "metadatas": [[]]
        }

    tokenized_question = question.lower().split()

    scores = bm25_index.get_scores(tokenized_question)

    # Return only chunks that match at least one query term
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    top_indices = [
        index for index in ranked_indices
        if scores[index] > 0
    ][:top_k]

    return {
        "documents": [[texts[i] for i in top_indices]],
        "metadatas": [
            [{"source": sources[i]} for i in top_indices]
        ]
    }
