import json
import re

from pydantic import BaseModel,Field 
from typing import List, Optional,Annotated , TypedDict
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv
from prompts import PLANNER_AGENT_PROMPT , SEARCH_AGENT_PROMPT ,EXECUTE_AGENT_PROMPT




load_dotenv()

llm_api_key=os.getenv("GROQ_API_KEY")
langsmith_api_key=os.getenv("LANGSMITH_API_KEY")

os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Agentic-AI-Proj")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
print("Tracing:", os.environ["LANGCHAIN_TRACING_V2"])
print("Project:", os.environ["LANGCHAIN_PROJECT"])





tools = [TavilySearch(max_results=5, api_key=os.getenv("TAVILY_API_KEY"))]
search_tool = tools[0]

model = ChatGroq(
    api_key=llm_api_key,
    model="groq/compound",
    temperature=0.2,
   
)


class RequestedItem(TypedDict):
    """What the user is asking to buy — no URL, just intent."""
    name: str        # e.g. "iPhone 15"
    category: str    # e.g. "electronics"
    budget: Optional[str]  # e.g. 1000 EGP

class Product(TypedDict):
    """A real search result — has a URL."""
    title: str
    url: str
    snippet: Optional[str]
    category: str

   
class AgentState(TypedDict):
    user_message: str
    budget: Optional[str]
    requested_items: Optional[List[RequestedItem]]   # ← planner fills this
    needs_clarification: bool
    products: Optional[List[Product]]                # ← search_node fills this
    final_answer: Optional[str]
    status: str




def _extract_json(text: str) -> Optional[dict]:
    """Best-effort extraction of a JSON object from an LLM response,
    in case the model wraps it in markdown fences or extra prose."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

def planner_node(state: AgentState) -> AgentState:
    """Ask the LLM to break the user's message into a list of RequestedItems."""
    print(f"[planner_node] received state: {state}")
 
    msgs = [
        SystemMessage(content=PLANNER_AGENT_PROMPT),
        HumanMessage(content=state["user_message"]),
    ]
    raw = model.invoke(msgs).content
    parsed = _extract_json(raw)
 
    raw_items = parsed.get("items") if parsed else None
 
    requested_items: List[RequestedItem] = []
    if raw_items:
        for entry in raw_items:
            name = entry.get("name")
            category = entry.get("category")
            if not name or not category:
                continue  # skip malformed entries rather than failing the whole plan
            requested_items.append(
                RequestedItem(
                    name=name,
                    category=category,
                    budget=entry.get("budget"),
                )
            )
 
    if not requested_items:
        new_state: AgentState = {
            **state,
            "requested_items": None,
            "categories": None,
            "budget": None,
            "needs_clarification": True,
            "status": "needs_clarification",
        }
    else:
        # Derive a flat, de-duplicated category list (search_node groups by category)
        # and an overall budget (largest per-item budget stated) for convenience/back-compat.
        categories = list(dict.fromkeys(item["category"] for item in requested_items))
        budgets = [item["budget"] for item in requested_items if item.get("budget")]
        overall_budget = max(budgets) if budgets else None
 
        new_state = {
            **state,
            "requested_items": requested_items,
            "categories": categories,
            "budget": overall_budget,
            "needs_clarification": False,
            "status": "planned",
        }
 
    print(f"[planner_node] returning state: {new_state}")
    return new_state
   






# def single_agent_answer(question: str) -> str:
#     msgs = [
#         SystemMessage(content=PLANNER_AGENT_PROMPT),
#         HumanMessage(content=question),
#     ]
#     return model.invoke(msgs).content

# question = "i want to buy a new iphone and a jacket , and I have a budget of $5000."
# print(single_agent_answer(question))
