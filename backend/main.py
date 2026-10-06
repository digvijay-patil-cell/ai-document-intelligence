from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import json

from agents.graph import graph
from langchain_core.messages import HumanMessage, AIMessage

from database.connection import get_db
from database.models import (
    Employee,
    ChatHistory,
    ChatSession
)

from services.title_generator import generate_chat_title

from database.redis_client import (
    get_cached_answer,
    set_cached_answer
)


app = FastAPI(
    title="AI Document Intelligence API",
    description="Enterprise Knowledge Assistant API",
    version="1.0.0"
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI Document Intelligence API is running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):
    question: str
    session_id: str


# =========================================================
# AGENT CHAT - TEST ENDPOINT
# =========================================================

@app.post("/agent-chat")
def agent_chat(request: ChatRequest):

    initial_state = {
        "question": request.question,
        "messages": [
            HumanMessage(content=request.question)
        ],
        "answer": "",
        "sources": []
    }

    result = graph.invoke(initial_state)

    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", [])
    }


# =========================================================
# MAIN CHAT
# =========================================================

@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Get previous messages for this session
    # -----------------------------------------------------

    previous_chats = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.session_id == request.session_id
        )
        .order_by(ChatHistory.id.asc())
        .all()
    )

    # -----------------------------------------------------
    # 2. Convert previous conversation into LangChain
    #    messages
    # -----------------------------------------------------

    conversation_messages = []

    for chat in previous_chats:

        conversation_messages.append(
            HumanMessage(
                content=chat.question
            )
        )

        conversation_messages.append(
            AIMessage(
                content=chat.answer
            )
        )

    # -----------------------------------------------------
    # 3. Check whether ChatSession already exists
    # -----------------------------------------------------

    chat_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == request.session_id
        )
        .first()
    )

    # =====================================================
    # 4. CHECK REDIS CACHE
    # =====================================================

    cached_result = get_cached_answer(
        request.session_id,
        request.question
    )

    # =====================================================
    # 5. RETURN CACHED RESPONSE
    # =====================================================

    if cached_result:

        answer = cached_result["answer"]
        sources = cached_result["sources"]

        # Create session if it does not exist
        if not chat_session:

            title = generate_chat_title(
                request.question
            )

            chat_session = ChatSession(
                session_id=request.session_id,
                title=title
            )

            db.add(chat_session)

        # Update session time
        chat_session.updated_at = datetime.utcnow()

        # Save cached response to chat history
        chat_record = ChatHistory(
            session_id=request.session_id,
            question=request.question,
            answer=answer,
            sources=json.dumps(sources)
        )

        db.add(chat_record)

        db.commit()
        db.refresh(chat_record)

        return {
            "answer": answer,
            "sources": sources,
            "cached": True
        }

    # =====================================================
    # 6. RUN LANGGRAPH AGENT
    # =====================================================

    initial_state = {

        "question": request.question,

        "messages": conversation_messages + [
            HumanMessage(
                content=request.question
            )
        ],

        "answer": "",

        "sources": []
    }

    result = graph.invoke(initial_state)

    answer = result["answer"]
    sources = result["sources"]

    # =====================================================
    # 7. STORE ANSWER IN REDIS
    # =====================================================

    set_cached_answer(
        request.session_id,
        request.question,
        answer,
        sources
    )

    # =====================================================
    # 8. CREATE CHAT SESSION
    # =====================================================

    if not chat_session:

        title = generate_chat_title(
            request.question
        )

        chat_session = ChatSession(
            session_id=request.session_id,
            title=title
        )

        db.add(chat_session)

    else:

        chat_session.updated_at = datetime.utcnow()

    # =====================================================
    # 9. SAVE CHAT HISTORY
    # =====================================================

    chat_record = ChatHistory(
        session_id=request.session_id,
        question=request.question,
        answer=answer,
        sources=json.dumps(sources)
    )

    db.add(chat_record)

    db.commit()
    db.refresh(chat_record)

    # =====================================================
    # 10. RETURN RESPONSE
    # =====================================================

    return {
        "answer": answer,
        "sources": sources,
        "cached": False
    }


# =========================================================
# GET CHAT SESSIONS
# =========================================================

@app.get("/chat/sessions")
def get_chat_sessions(
    db: Session = Depends(get_db)
):

    sessions = (
        db.query(ChatSession)
        .order_by(
            ChatSession.updated_at.desc()
        )
        .all()
    )

    result = []

    for session in sessions:

        result.append({
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        })

    return result


# =========================================================
# CHAT HISTORY FOR ONE SESSION
# =========================================================

@app.get("/chat/history")
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):

    history = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.session_id == session_id
        )
        .order_by(
            ChatHistory.id.asc()
        )
        .all()
    )

    result = []

    for chat in history:

        sources = []

        if chat.sources:

            sources = json.loads(
                chat.sources
            )

        result.append({
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "sources": sources,
            "created_at": chat.created_at
        })

    return result


# =========================================================
# GET ALL EMPLOYEES
# =========================================================

@app.get("/employees")
def get_employees(
    db: Session = Depends(get_db)
):

    employees = db.query(Employee).all()

    return employees


# =========================================================
# GET ONE EMPLOYEE
# =========================================================

@app.get("/employees/{employee_id}")
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )

    if not employee:

        return {
            "message": "Employee not found"
        }

    return employee


# =========================================================
# CREATE EMPLOYEE
# =========================================================

class EmployeeCreate(BaseModel):

    employee_id: str
    name: str
    department: str
    email: str
    leave_balance: int


@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):

    new_employee = Employee(
        employee_id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        email=employee.email,
        leave_balance=employee.leave_balance
    )

    db.add(new_employee)

    db.commit()

    db.refresh(new_employee)

    return new_employee


# =========================================================
# UPDATE EMPLOYEE
# =========================================================

class EmployeeUpdate(BaseModel):

    name: str
    department: str
    email: str
    leave_balance: int


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )

    if not employee:

        return {
            "message": "Employee not found"
        }

    employee.name = employee_data.name
    employee.department = employee_data.department
    employee.email = employee_data.email
    employee.leave_balance = employee_data.leave_balance

    db.commit()

    db.refresh(employee)

    return employee


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )

    if not employee:

        return {
            "message": "Employee not found"
        }

    db.delete(employee)

    db.commit()

    return {
        "message": "Employee deleted successfully",
        "employee_id": employee_id
    }