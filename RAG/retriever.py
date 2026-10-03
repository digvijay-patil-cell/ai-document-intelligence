from sentence_transformers import SentenceTransformer
import chromadb


# Load the same embedding model used during storage
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# Connect to existing ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")


# Get existing collection
collection = chroma_client.get_collection(
    name="enterprise_documents"
)


def retrieve_documents(question, top_k=3):

    # Convert user question into an embedding
    question_embedding = embedding_model.encode(question).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results


if __name__ == "__main__":

    question = "How many casual leaves are available per year?"

    results = retrieve_documents(question)

    print("\nQUESTION:")
    print(question)

    print("\nRETRIEVED DOCUMENTS:")

    for i in range(len(results["documents"][0])):

        print("\n------------------------------")
        print("RESULT", i + 1)
        print("------------------------------")

        print("Source:", results["metadatas"][0][i]["source"])
        print("Text:")
        print(results["documents"][0][i])