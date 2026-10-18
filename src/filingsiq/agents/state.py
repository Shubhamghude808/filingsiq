"""Phase 3: planner / specialist / critic agents (LangGraph) live here."""
from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str
    plan: list[str]
    evidence: list[dict]
    draft_answer: str
    verified: bool
