import streamlit as st
import requests
import uuid


# =========================================================
# CONFIG
# =========================================================

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Document Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .source-box {
            background: #f7f7f8;
            padding: 0.7rem 1rem;
            border-radius: 0.6rem;
            margin-top: 0.5rem;
        }

        .history-title {
            font-size: 0.95rem;
            font-weight: 500;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False


# =========================================================
# API FUNCTIONS
# =========================================================

def check_api():

    try:

        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5
        )

        if response.status_code == 200:
            return True

    except requests.RequestException:
        pass

    return False


# =========================================================
# LOAD ONE CHAT HISTORY
# =========================================================

def load_chat_history(session_id):

    try:

        response = requests.get(
            f"{API_BASE_URL}/chat/history",
            params={
                "session_id": session_id
            },
            timeout=10
        )

        if response.status_code == 200:

            history = response.json()

            messages = []

            for item in history:

                messages.append({
                    "role": "user",
                    "content": item["question"]
                })

                messages.append({
                    "role": "assistant",
                    "content": item["answer"],
                    "sources": item.get(
                        "sources",
                        []
                    )
                })

            return messages

    except requests.RequestException:
        pass

    return []


# =========================================================
# LOAD ALL CHAT SESSIONS
# =========================================================

def load_chat_sessions():

    try:

        response = requests.get(
            f"{API_BASE_URL}/chat/sessions",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

    except requests.RequestException:
        pass

    return []


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(question):

    try:

        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "question": question,
                "session_id": st.session_state.session_id
            },
            timeout=120
        )

        if response.status_code == 200:
            return response.json()

        return {
            "error": (
                f"API returned status code "
                f"{response.status_code}"
            )
        }

    except requests.RequestException as e:

        return {
            "error": str(e)
        }


# =========================================================
# LOAD CURRENT CHAT ON FIRST RUN
# =========================================================

if not st.session_state.history_loaded:

    st.session_state.messages = load_chat_history(
        st.session_state.session_id
    )

    st.session_state.history_loaded = True


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🤖 Enterprise Assistant")

    st.markdown("---")

    # -----------------------------------------------------
    # SYSTEM STATUS
    # -----------------------------------------------------

    st.markdown("### System Status")

    if check_api():

        st.success("FastAPI: Connected")

    else:

        st.error("FastAPI: Offline")

    st.markdown("---")

    # -----------------------------------------------------
    # NEW CONVERSATION
    # -----------------------------------------------------

    if st.button(
        "🆕 New Conversation",
        use_container_width=True
    ):

        # Create completely new session
        st.session_state.session_id = str(
            uuid.uuid4()
        )

        # Clear current messages
        st.session_state.messages = []

        # Mark history as already handled
        st.session_state.history_loaded = True

        st.rerun()

    st.markdown("---")

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    st.markdown("### History")

    chat_sessions = load_chat_sessions()

    if chat_sessions:

        for session in chat_sessions:

            session_id = session.get(
                "session_id"
            )

            title = session.get(
                "title",
                "New Conversation"
            )

            # Show ONLY title
            if st.button(
                title,
                key=f"history_{session_id}",
                use_container_width=True
            ):

                # Switch to selected conversation
                st.session_state.session_id = (
                    session_id
                )

                # Load selected conversation
                st.session_state.messages = (
                    load_chat_history(
                        session_id
                    )
                )

                st.session_state.history_loaded = True

                st.rerun()

    else:

        st.caption(
            "No previous conversations."
        )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    'AI Document Intelligence & Enterprise Knowledge Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about company policies, employee information, '
    'benefits, IT procedures and more.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# QUICK QUESTIONS
# =========================================================

st.markdown("### Quick Questions")

quick_questions = [
    "How many casual leaves are available per year?",
    "What is the leave balance of EMP001?",
    "What is the standard probation period?",
    "What documents are required during onboarding?"
]

cols = st.columns(4)

for index, question_text in enumerate(
    quick_questions
):

    if cols[index].button(
        question_text,
        use_container_width=True,
        key=f"quick_{index}"
    ):

        st.session_state.pending_question = (
            question_text
        )


# =========================================================
# CHAT DISPLAY
# =========================================================

st.markdown("---")

st.markdown("### 💬 Conversation")

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        # Show sources only for assistant messages
        if message["role"] == "assistant":

            sources = message.get(
                "sources",
                []
            )

            if sources:

                with st.expander(
                    "📄 Sources"
                ):

                    for source in sources:

                        st.write(
                            f"• {source}"
                        )


# =========================================================
# QUESTION INPUT
# =========================================================

question = st.chat_input(
    "Ask your question..."
)


# =========================================================
# QUICK QUESTION HANDLING
# =========================================================

if "pending_question" in st.session_state:

    question = st.session_state.pop(
        "pending_question"
    )


# =========================================================
# SEND QUESTION
# =========================================================

if question:

    question = question.strip()

    if question:

        # -------------------------------------------------
        # Show user question
        # -------------------------------------------------

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        # -------------------------------------------------
        # Call FastAPI
        # -------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                result = ask_question(
                    question
                )

            # -------------------------------------------------
            # API ERROR
            # -------------------------------------------------

            if "error" in result:

                answer = (
                    "I could not connect to the "
                    "FastAPI backend. Please make sure "
                    "the FastAPI server is running."
                )

                st.error(
                    result["error"]
                )

                sources = []

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            else:

                answer = result.get(
                    "answer",
                    "No answer returned."
                )

                sources = result.get(
                    "sources",
                    []
                )

                st.markdown(answer)

                if sources:

                    with st.expander(
                        "📄 Sources"
                    ):

                        for source in sources:

                            st.write(
                                f"• {source}"
                            )

        # -------------------------------------------------
        # Save assistant response
        # -------------------------------------------------

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

        # Refresh UI
        st.rerun()