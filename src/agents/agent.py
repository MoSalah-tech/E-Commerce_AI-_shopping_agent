import json
import re

from pydantic import BaseModel,Field 
from typing import Optional, TypedDict, Dict, Any, List
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









class AgentState(TypedDict):
    user_message: str
    planner: Optional[Dict[str, Any]]
    search_results: List[Dict]
    final_answer: Optional[str]



class Planner(BaseModel):
    product_name: str = Field(..., description="The name of the product extracted from the user message.")
    categories: List[str] = Field(..., description="List of product categories extracted from the user message.")
    budget: str = Field(..., description="The user's overall budget for shopping.")



class Product(BaseModel):
    name: str = Field(..., description="Name/title of the product as listed by the seller.")
    price: Optional[str] = Field(None, description="Price of the product, if available.")
    purchase_link: str = Field(..., description="Direct URL where the user can buy this exact product (not a homepage or search page).")
    source: Optional[str] = Field(None, description="Name of the retailer/website selling the product.")
    description: Optional[str] = Field(None, description="Short one-sentence description of the product.")
 
 
class SearchOutput(BaseModel):
    query: str = Field(..., description="The search query used to find these products.")
    products: List[Product] = Field(..., description="Products matching what the user wants to buy, each with a direct purchase link.")
    


tools = [TavilySearch(max_results=5, api_key=os.getenv("TAVILY_API_KEY"))]
search_tool = tools[0]

model = ChatGroq(
    api_key=llm_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
   
)



def planner_node(state: AgentState) -> AgentState:
    structured_planner = model.with_structured_output(Planner)
    plan_obj = structured_planner.invoke([
        SystemMessage(content=PLANNER_AGENT_PROMPT),
        HumanMessage(content=state["user_message"]),
    ])
    state["planner"] = plan_obj.model_dump()
    state["search_attempts"] = 0
    state.setdefault("max_search_attempts", 2)
    return state


print("Planner node test:")
test_state = {"user_message": "I want to buy a new laptop and black leather jacket. I want the laptop to be good for gaming and programming, and I have a budget of $1500."}
test_state = planner_node(test_state)
print("Planner output:", test_state["planner"])










# def single_agent_answer(question: str) -> str:
#     msgs = [
#         SystemMessage(content=PLANNER_AGENT_PROMPT),
#         HumanMessage(content=question),
#     ]
#     return model.invoke(msgs).content

# question = "i want to buy a new iphone and a jacket , and I have a budget of $5000."
# print(single_agent_answer(question))
