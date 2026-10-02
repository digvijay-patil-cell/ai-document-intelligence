from sentence_transformers import SentenceTransformer
import chromadb
import hashlib

from document_chunker import process_all_documents


# --------------------------------
# 1. Load Embedding Model
# --------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# --------------------------------
# 2. Create ChromaDB Client
# --------------------------------

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)


# --------------------------------
# 3. Create or Get Collection
# --------------------------------

collection = chroma_client.get_or_create_collection(
    name="enterprise_documents"
)


# --------------------------------
# 4. Generate Stable Chunk ID
# --------------------------------

def create_chunk_id(source, chunk_index):

    value = f"{source}_{chunk_index}"

    return hashlib.md5(
        value.encode("utf-8")
    ).hexdigest()


# --------------------------------
# 5. Store Embeddings
# --------------------------------

def store_embeddings():

    # Get all document chunks
    chunks = process_all_documents()

    documents = []
    embeddings = []
    metadatas = []
    ids = []

    # --------------------------------
    # Create embeddings
    # --------------------------------

    for i, chunk in enumerate(chunks):

        text = chunk["text"]
        source = chunk["source"]

        # Convert text into numerical vector
        embedding = embedding_model.encode(
            text
        ).tolist()

        documents.append(text)

        embeddings.append(embedding)

        metadatas.append({
            "source": source
        })

        # Stable ID
        chunk_id = create_chunk_id(
            source,
            i
        )

        ids.append(chunk_id)

    # --------------------------------
    # Store / Update in ChromaDB
    # --------------------------------

    collection.upsert(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    # --------------------------------
    # Remove old chunks
    # --------------------------------

    existing_data = collection.get()

    existing_ids = existing_data.get(
        "ids",
        []
    )

    current_ids = set(ids)

    old_ids = [
        chunk_id
        for chunk_id in existing_ids
        if chunk_id not in current_ids
    ]

    if old_ids:

        collection.delete(
            ids=old_ids
        )

        print(
            "Old chunks removed:",
            len(old_ids)
        )

    # --------------------------------
    # Final Information
    # --------------------------------

    print(
        "Embeddings created:",
        len(embeddings)
    )

    print(
        "Documents stored in ChromaDB:",
        len(documents)
    )

    print(
        "Total chunks in ChromaDB:",
        collection.count()
    )


# --------------------------------
# 6. Run Ingestion
# --------------------------------

if __name__ == "__main__":

    store_embeddings()