import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

# __________________ Agent State Definition ______________________

class AgentState(TypedDict):
    user_message: str
    # operator.add reducer: each node's returned chat_history entries are
    # CONCATENATED onto the existing value, not overwritten. Every node MUST
    # return only the NEW entries it wants to add (or omit the key entirely
    # if it isn't adding any) — never the whole accumulated list, or it will
    # be double-counted. See exceuter_node in graph.py for the only node that
    # actually sets this.
    chat_history: Annotated[List[Dict[str, str]], operator.add]
    planner: Optional[Dict[str, Any]]
    search_results: List[Dict]
    final_answer: Optional[str]
