from typing import Annotated, List, Optional, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tools: Optional[list[BaseTool]]