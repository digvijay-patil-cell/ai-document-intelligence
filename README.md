\# AI Document Intelligence \& Enterprise Knowledge Assistant



An AI-powered enterprise knowledge assistant that answers questions from company documents using Retrieval-Augmented Generation (RAG). It provides contextual answers with source references through a web-based chat interface.



\## 🚀 Live Demo



\- \*\*Streamlit Application:\*\* \[Open Live App](https://ai-document-intelligence-qk7tiujwayzxymfmieruub.streamlit.app/)

\- \*\*Backend API:\*\* \[Open Backend](https://ai-document-intelligence-ebhp.onrender.com)

\- \*\*API Documentation:\*\* \[Open Swagger UI](https://ai-document-intelligence-ebhp.onrender.com/docs)



\## ✨ Features



\- Document-based question answering for company policies and employee guidelines.

\- Retrieval-Augmented Generation (RAG) for context-aware answers.

\- Source document references in responses.

\- LangGraph-based AI agent workflow.

\- FastAPI REST API for frontend-backend communication.

\- PostgreSQL-backed chat history and session management.

\- Redis caching with graceful handling when the cache is unavailable.

\- Streamlit dashboard for interactive conversations.

\- PDF document processing and semantic retrieval.



\## 🛠️ Technology Stack



\- \*\*Programming Language:\*\* Python

\- \*\*Frontend:\*\* Streamlit

\- \*\*Backend:\*\* FastAPI

\- \*\*LLM Integration:\*\* LangChain, Groq

\- \*\*Agent Workflow:\*\* LangGraph

\- \*\*RAG and Embeddings:\*\* Sentence Transformers

\- \*\*Vector Database:\*\* ChromaDB

\- \*\*Relational Database:\*\* PostgreSQL

\- \*\*Caching:\*\* Redis

\- \*\*PDF Processing:\*\* PyPDF

\- \*\*API Testing:\*\* Swagger UI, Postman

\- \*\*Version Control:\*\* Git, GitHub

\- \*\*Deployment:\*\* Streamlit Community Cloud, Render



\## 🏗️ System Architecture



1\. \*\*Document Loading:\*\* Loads company policy and employee-guidance PDFs.

2\. \*\*Text Extraction and Chunking:\*\* Extracts PDF text and divides it into smaller chunks.

3\. \*\*Embedding Generation:\*\* Converts text chunks into vector representations.

4\. \*\*Vector Retrieval:\*\* Retrieves relevant document content from ChromaDB.

5\. \*\*Answer Generation:\*\* Uses retrieved context to generate answers with an LLM.

6\. \*\*Agent Workflow:\*\* Uses LangGraph to coordinate the question-answering process.

7\. \*\*REST API:\*\* FastAPI receives questions and returns answers and source references.

8\. \*\*Database and Cache:\*\* PostgreSQL stores conversation records, while Redis provides optional response caching.

9\. \*\*Web Interface:\*\* Streamlit provides the user-facing dashboard.



\## 📂 Project Structure



```text

ai-document-intelligence/

├── agents/

├── backend/

├── database/

├── documents/

├── frontend/

│   ├── app.py

│   └── requirements.txt

├── RAG/

├── services/

├── requirements.txt

├── requirements-render.txt

└── README.md

```



\## ⚙️ Local Installation and Setup



\### 1. Clone the Repository



```bash

git clone https://github.com/digvijay-patil-cell/ai-document-intelligence.git

cd ai-document-intelligence

```



\### 2. Create and Activate the Conda Environment



```bash

conda create -n ai\_document python=3.11

conda activate ai\_document

```



If the environment already exists, activate it instead of creating it again.



\### 3. Install Dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure Environment Variables



Create a local `.env` file containing the required LLM API key and database/cache connection settings.



Keep API keys and credentials private. Never commit your `.env` file to GitHub.



\### 5. Run the Backend



```bash

uvicorn backend.main:app --reload

```



Open the local API documentation:



\[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



\### 6. Run the Frontend



Open a second terminal, activate the `ai\_document` environment, and run:



```bash

streamlit run frontend/app.py

```



The frontend uses `http://127.0.0.1:8000` by default. For deployment, configure `API\_BASE\_URL` to point to the deployed backend.



\## 🧪 Example



\*\*Question:\*\* How many casual leave days are available per year?



\*\*Answer:\*\* Eligible full-year employees are entitled to 12 casual leave days per calendar year.



\*\*Source Documents:\*\*



\- `Leave\_and\_Time-Off\_Policy.pdf`

\- `Employee\_Handbook.pdf`



\## 🔐 Security



\- Keep API keys and database credentials in environment variables or deployment secrets.

\- Never commit `.env` files, credentials, or confidential documents.

\- Configure appropriate access controls before using real company documents.



\## 👨‍💻 Author



\*\*Digvijay Patil\*\*



\- \*\*GitHub:\*\* \[digvijay-patil-cell](https://github.com/digvijay-patil-cell)

\- \*\*LinkedIn:\*\* \[Digvijay Patil](https://linkedin.com/in/digvijay-patil-901935292/)



\## 🎯 Project Objective



This project demonstrates the integration of Retrieval-Augmented Generation (RAG), large language models, AI agent workflows, vector search, REST APIs, relational databases, caching, and cloud deployment to build an enterprise document question-answering assistant.



