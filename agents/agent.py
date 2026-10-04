from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.tools import (
    search_documents,
    get_employee_information
)

import json


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CREATE LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# =========================================================
# AVAILABLE TOOLS
# =========================================================

tools = [
    search_documents,
    get_employee_information
]


# =========================================================
# GIVE TOOLS TO LLM
# =========================================================

llm_with_tools = llm.bind_tools(tools)


# =========================================================
# TOOL NODE
# =========================================================

tool_node = ToolNode(tools)


# =========================================================
# SYSTEM INSTRUCTIONS
# =========================================================

SYSTEM_PROMPT = """
You are an Enterprise Knowledge Assistant.

Your job is to answer employee questions using:
1. Previous conversation context
2. Enterprise documents through the search_documents tool
3. Employee information through the get_employee_information tool

IMPORTANT RULES:

1. Never invent or assume information.

2. Only provide information that is available in:
   - the conversation
   - enterprise documents
   - employee data returned by the tools

3. If information is not available, clearly say that the
   information is not available.

4. Do not calculate or guess an employee-specific value
   when the required data is missing.

5. Keep policy information and employee-specific information
   separate.

Example:
- Company policy says employees receive 12 casual leaves/year.
- Employee data says EMP001 has 8 total leave days remaining.

Do NOT assume that EMP001 has 8 casual leaves remaining.

6. If the user asks a follow-up question such as:
   "What about casual leaves?"
   use the previous conversation to understand what
   the user is referring to.

7. When the question requires employee information,
   use the get_employee_information tool.

8. When the question requires information from company
   documents or policies, use the search_documents tool.

9. When a question requires both employee information
   and company policy information, use both tools.

10. Give a clear and concise answer.

11. Never mention internal tool names, LangGraph,
    vector databases, or implementation details to the user.
"""


# =========================================================
# AGENT NODE
# =========================================================

def agent_node(state: AgentState):

    # System instruction + previous conversation + current question
    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    # Send messages to LLM
    response = llm_with_tools.invoke(messages)

    # Add LLM response to State
    return {
        "messages": [response]
    }


# =========================================================
# DECIDE WHETHER TO USE A TOOL OR FINISH
# =========================================================

def should_continue(state: AgentState):

    # Get latest message
    last_message = state["messages"][-1]

    # Check whether LLM requested a tool
    if last_message.tool_calls:
        return "tools"

    # Otherwise finish
    return END


# =========================================================
# FINAL ANSWER NODE
# =========================================================

def final_answer_node(state: AgentState):

    # Get final AI message
    last_message = state["messages"][-1]

    # Extract final answer
    answer = last_message.content

    # Collect sources
    sources = []

    for message in state["messages"]:

        # ToolMessage contains tool result
        if message.type == "tool":

            tool_result = message.content

            try:
                # Tool result is normally JSON string
                data = json.loads(tool_result)

                for source in data.get("sources", []):

                    if source not in sources:
                        sources.append(source)

            except (json.JSONDecodeError, TypeError):

                # If tool result doesn't contain sources,
                # simply continue.
                pass

    return {
        "answer": answer,
        "sources": sources
    }


# =========================================================
# CREATE LANGGRAPH
# =========================================================

graph_builder = StateGraph(AgentState)


# =========================================================
# ADD NODES
# =========================================================

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tools",
    tool_node
)

graph_builder.add_node(
    "final_answer",
    final_answer_node
)


# =========================================================
# START → AGENT
# =========================================================

graph_builder.add_edge(
    START,
    "agent"
)


# =========================================================
# AGENT → TOOLS OR FINAL ANSWER
# =========================================================

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: "final_answer"
    }
)


# =========================================================
# TOOLS → AGENT
# =========================================================

graph_builder.add_edge(
    "tools",
    "agent"
)


# =========================================================
# FINAL ANSWER → END
# =========================================================

graph_builder.add_edge(
    "final_answer",
    END
)


# =========================================================
# COMPILE GRAPH
# =========================================================

graph = graph_builder.compile()


# =========================================================
# TEST COMPLETE AGENT
# =========================================================

if __name__ == "__main__":

    test_state = {

        "question": "What is the leave balance of EMP001?",

        "messages": [
            HumanMessage(
                content="What is the leave balance of EMP001?"
            )
        ],

        "answer": "",

        "sources": []
    }

    result = graph.invoke(test_state)

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(result["answer"])

    print("\n==============================")
    print("SOURCES")
    print("==============================")

    for source in result["sources"]:
        print("📄",source)