import warnings
from pydantic import BaseModel,Field
from typing import List, Optional,Annotated
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph
import os
from dotenv import load_dotenv
from prompts import PLANNER_AGENT 

load_dotenv()

api_key=os.getenv("GROQ_API_KEY")






model = ChatGroq(
    api_key=api_key,
    model="groq/compound",
    temperature=0.2,
   
)




def single_agent_answer(question: str) -> str:
    msgs = [
        SystemMessage(content=PLANNER_AGENT),
        HumanMessage(content=question),
    ]
    return model.invoke(msgs).content

question = "i want to buy a pizza and a diet coke , and I have a budget of $50."
print(single_agent_answer(question))
