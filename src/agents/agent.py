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





tools = [TavilySearch(max_results=5, api_key=os.getenv("TAVILY_API_KEY"))]
search_tool = tools[0]

model = ChatGroq(
    api_key=llm_api_key,
    model="groq/compound",
    temperature=0.2,
   
)



class AgentState(TypedDict):
    user_message: str
    planner: Optional[Dict[str, Any]]
    search_results: List[Dict]
    final_answer: Optional[str]



class PlannerOutput(BaseModel):
    product_name: str = Field(..., description="The name of the product extracted from the user message.")
    categories: List[str] = Field(..., description="List of product categories extracted from the user message.")
    budget: str = Field(..., description="The user's overall budget for shopping.")
    






# def single_agent_answer(question: str) -> str:
#     msgs = [
#         SystemMessage(content=PLANNER_AGENT_PROMPT),
#         HumanMessage(content=question),
#     ]
#     return model.invoke(msgs).content

# question = "i want to buy a new iphone and a jacket , and I have a budget of $5000."
# print(single_agent_answer(question))
