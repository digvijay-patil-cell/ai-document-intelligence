from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


def generate_chat_title(question):
    prompt = f"""
Create a short title for this conversation.

Rules:
- Maximum 5 words
- Keep it clear and meaningful
- Do not use quotes
- Do not include "Chat", "Conversation", or "Question"
- The title should describe the main topic

User question:
{question}

Return only the title.
"""

    response = llm.invoke(prompt)

    title = response.content.strip()

    return title