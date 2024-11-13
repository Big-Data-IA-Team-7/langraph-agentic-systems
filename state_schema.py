from typing import Annotated, Sequence
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing import Literal

from langchain_core.messages import BaseMessage

from langchain_core.agents import AgentAction
import operator

class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

class grade(BaseModel):
    """Binary score for relevance check."""

    binary_score: str = Field(description="Relevance score 'yes' or 'no'")

class RouteResponse(BaseModel):
    next: Literal["WebSearch", "RAGAgent", "FINISH"]