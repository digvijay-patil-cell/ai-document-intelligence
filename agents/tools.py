from langchain_core.tools import tool

from RAG.retriever import retrieve_documents
from database.connection import SessionLocal
from database.models import Employee


@tool
def search_documents(question: str):
    """
    Search company documents using ChromaDB and return relevant
    document chunks along with their source PDF names.
    """

    results = retrieve_documents(question)

    # Get retrieved document chunks
    documents = results["documents"][0]

    # Get metadata of retrieved chunks
    metadatas = results["metadatas"][0]

    # Store unique source PDF names
    sources = []

    for metadata in metadatas:
        source = metadata["source"]

        if source not in sources:
            sources.append(source)

    return {
        "documents": documents,
        "sources": sources
    }


@tool
def get_employee_information(employee_id: str):
    """
    Get employee information from the PostgreSQL database
    using the employee ID.
    """

    # Create database session
    db = SessionLocal()

    # Search employee by employee ID
    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    # If employee does not exist
    if not employee:
        db.close()

        return {
            "message": "Employee not found"
        }

    # Store employee information before closing session
    employee_data = {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "department": employee.department,
        "email": employee.email,
        "leave_balance": employee.leave_balance
    }

    # Close database session
    db.close()

    return employee_data


# Test the tools
if __name__ == "__main__":

    print("\n==============================")
    print("Testing Search Documents Tool")
    print("==============================")

    result = search_documents.invoke({
        "question": "How many casual leaves are available per year?"
    })

    print("\nDocuments:")
    print(result["documents"])

    print("\nSources:")
    print(result["sources"])


    print("\n==============================")
    print("Testing Employee Information Tool")
    print("==============================")

    result = get_employee_information.invoke({
        "employee_id": "EMP001"
    })

    print("\nEmployee Information:")
    print(result)