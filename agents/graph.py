import json

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

from agents.state import AgentState
from agents.agent import agent_node
from agents.tools import (
    search_documents,
    get_employee_information
)


# --------------------------------
# 1. Available Tools
# --------------------------------

tools = [
    search_documents,
    get_employee_information
]


# --------------------------------
# 2. Create Tool Node
# --------------------------------

tool_node = ToolNode(tools)


# --------------------------------
# 3. Decide what happens
#    after Agent Node
# --------------------------------

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    # If Agent requested a tool
    if last_message.tool_calls:
        return "tools"

    # If Agent has final answer
    return END


# --------------------------------
# 4. Final Answer Node
# --------------------------------

def final_answer(state: AgentState):

    # Last message should be the final AI response
    last_message = state["messages"][-1]

    answer = last_message.content

    sources = []

    # Find sources from ToolMessage
    for message in state["messages"]:

        if message.type == "tool":

            try:
                # Safely convert JSON string into Python dictionary
                tool_result = json.loads(message.content)

                # Get sources from tool result
                for source in tool_result.get("sources", []):

                    if source not in sources:
                        sources.append(source)

            except (json.JSONDecodeError, TypeError):
                # Ignore tool results that are not valid JSON
                pass

    return {
        "answer": answer,
        "sources": sources
    }


# --------------------------------
# 5. Create Graph
# --------------------------------

graph_builder = StateGraph(AgentState)


# --------------------------------
# 6. Add Nodes
# --------------------------------

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
    final_answer
)


# --------------------------------
# 7. START → Agent
# --------------------------------

graph_builder.add_edge(
    START,
    "agent"
)


# --------------------------------
# 8. Agent → Tools OR Final Answer
# --------------------------------

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: "final_answer"
    }
)


# --------------------------------
# 9. Tools → Agent
# --------------------------------

graph_builder.add_edge(
    "tools",
    "agent"
)


# --------------------------------
# 10. Final Answer → END
# --------------------------------

graph_builder.add_edge(
    "final_answer",
    END
)


# --------------------------------
# 11. Compile Graph
# --------------------------------

graph = graph_builder.compile()


# --------------------------------
# 12. Test Graph
# --------------------------------

if __name__ == "__main__":

    question = "How many casual leaves are available per year?"

    initial_state = {
        "question": question,

        "messages": [
            HumanMessage(
                content=question
            )
        ],

        "answer": "",

        "sources": []
    }

    result = graph.invoke(initial_state)


    # --------------------------------
    # Print Final Answer
    # --------------------------------

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(result["answer"])


    # --------------------------------
    # Print Sources
    # --------------------------------

    print("\n==============================")
    print("SOURCES")
    print("==============================")

    for source in result["sources"]:
        print("📄", source)


    # --------------------------------
    # Print Message History
    # --------------------------------

    print("\n==============================")
    print("MESSAGE HISTORY")
    print("==============================")

    for message in result["messages"]:

        print("\n------------------------------")

        print(
            type(message).__name__,
            ":",
            message.content
        )