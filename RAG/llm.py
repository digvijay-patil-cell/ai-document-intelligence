import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


def generate_answer(question, context):

    prompt = f"""
act like enterprise knowledge assistant.

Answer the user's question using only the provided context.

If the answer is not available in the context, say:
"I could not find this information in the provided documents.
strictly avoid wroung answers"

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    question = "How many casual leave days are available per year?"

    context = """
    Employees are entitled to 12 casual leave days per calendar year.
    """

    answer = generate_answer(question, context)

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")
    print(answer)