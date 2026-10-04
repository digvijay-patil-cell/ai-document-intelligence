from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    question: str
    messages: Annotated[list[AnyMessage], add_messages]
    answer: str
    sources: list