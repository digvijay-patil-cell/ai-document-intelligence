from RAG.retriever import retrieve_documents
from RAG.llm import generate_answer


def answer_question(question):

    # 1. Search ChromaDB
    results = retrieve_documents(question)

    # 2. Get retrieved document chunks
    documents = results["documents"][0]

    # 3. Get source information
    metadatas = results["metadatas"][0]

    # 4. Combine chunks into context
    context = "\n\n".join(documents)

    # 5. Generate answer using LLM
    answer = generate_answer(question, context)

    # 6. Get unique source names
    sources = []

    for metadata in metadatas:
        source = metadata["source"]

        if source not in sources:
            sources.append(source)

    return answer, sources


# Interactive chatbot
if __name__ == "__main__":

    print("===================================")
    print("   Enterprise Knowledge Assistant")
    print("===================================")

    while True:

        question = input("\nAsk your question: ")

        # Exit
        if question.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        # Get answer and sources
        answer, sources = answer_question(question)

        print("\nAnswer:")
        print(answer)

        print("\nSource:")

        for source in sources:
            print("📄", source)
 