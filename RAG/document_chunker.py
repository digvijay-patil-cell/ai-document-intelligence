from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from document_loader import load_pdf


# Folder containing all PDF documents
DOCUMENTS_DIR = Path("documents")


def create_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_text(text)

    return chunks


def process_all_documents():
    all_chunks = []

    # Find all PDF files inside documents folder
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    print("Total PDF files:", len(pdf_files))

    for pdf_file in pdf_files:

        print("\nProcessing:", pdf_file.name)

        # Extract text from PDF
        text = load_pdf(pdf_file)

        # Create chunks
        chunks = create_chunks(text)

        # Add source information to every chunk
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": pdf_file.name
            })

        print("Chunks created:", len(chunks))

    return all_chunks


if __name__ == "__main__":

    chunks = process_all_documents()

    print("\n==============================")
    print("TOTAL CHUNKS:", len(chunks))
    print("==============================")

    # Display first 5 chunks
    for i, chunk in enumerate(chunks[:5]):

        print("\n------------------------------")
        print("CHUNK", i + 1)
        print("------------------------------")

        print("Source:", chunk["source"])
        print("Text:")
        print(chunk["text"])