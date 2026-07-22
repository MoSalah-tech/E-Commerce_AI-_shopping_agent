import os
import sys
import asyncio

if sys.platform == "win32":     # new
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # new



from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, TypedDict, Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from Serpapi import shopping_search
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from prompts import *


load_dotenv()

llm_api_key = os.getenv("GROQ_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
postgres_url = os.getenv("POSTGRES_URL")

os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Agentic-AI-Proj")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
print("Tracing:", os.environ["LANGCHAIN_TRACING_V2"])
print("Project:", os.environ["LANGCHAIN_PROJECT"])


# __________________ Agent State Definition ______________________

class AgentState(TypedDict):
    user_message: str
    chat_history: List[Dict[str, str]]
    planner: Optional[Dict[str, Any]]
    search_results: List[Dict]
    final_answer: Optional[str]


# __________________________ Structured Output Models ______________________

class Planner(BaseModel):
    product_name: List[str] = Field(..., description="The name of each product extracted from the user message.")
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


class Recommendation(BaseModel):
    product_name: str = Field(..., description="The recommended product.")
    reason: str = Field(..., description="Why this product was chosen.")
    purchase_link: str = Field(..., description="Direct purchase link.")
    price: Optional[str] = Field(None)
    source: Optional[str] = Field(None)


class ExecuterOutput(BaseModel):
    recommendation: List[Recommendation]
    summary: str = Field(..., description="Overall shopping recommendation")


# __________________________ Agent Setup ______________________

# __________________________ Tavily Search ______________________
tools = [TavilySearch(max_results=5, api_key=os.getenv("TAVILY_API_KEY"))]
search_tool = tools[0]


model = ChatGroq(
    api_key=llm_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)


# ___________________________ Planner Node ______________________
def planner_node(state: AgentState) -> AgentState:
    structured_planner = model.with_structured_output(Planner)

    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in state.get("chat_history", [])
    )

    plan_obj = structured_planner.invoke([
        SystemMessage(content=PLANNER_AGENT_PROMPT),
        HumanMessage(content=f"""
Conversation so far:
{history_text}

Latest message:
{state["user_message"]}
"""),
    ])
    state["planner"] = plan_obj.model_dump()
    return state


# ___________________________ Search node Using Tavily Search _____________________

def search_node(state: AgentState) -> AgentState:
    planner = state["planner"]

    # -----------------------------
    # Build search query
    # -----------------------------
    query = f"""
    {planner["product_name"]}

    Categories:
    {", ".join(planner["categories"])}

    Budget:
    {planner["budget"]}

    Find products for purchase.
    """

    # -----------------------------
    # Search Tavily
    # -----------------------------
    tavily_results = search_tool.invoke(query)

    # -----------------------------
    # Convert search results into text
    # -----------------------------
    context = ""

    for i, result in enumerate(tavily_results["results"], start=1):
        context += f"""
Product {i}

Title:
{result.get("title")}

URL:
{result.get("url")}

Content:
{result.get("content")}

"""

    # -----------------------------
    # Ask LLM to structure results
    # -----------------------------
    structured_search = model.with_structured_output(SearchOutput)

    search_output = structured_search.invoke([
        SystemMessage(content=SEARCH_AGENT_PROMPT),
        HumanMessage(
            content=f"""
User request:
{state["user_message"]}

Search Query:
{query}

Web Results:
{context}
"""
        )
    ])

    state["search_results"] = search_output.model_dump()

    return state


# _________________________ Search Node using SerpApi ____________________________

# With SerpAPI, you already receive structured product data. The LLM would just be reformatting JSON, which is unnecessary.

# def search_node(state: AgentState) -> AgentState:
#
#     planner = state["planner"]
#
#     all_results = []
#
#     for product in planner["product_name"]:
#
#         shopping_results = shopping_search(product)
#
#         products = []
#
#         for item in shopping_results:
#
#             products.append(
#                 Product(
#                     name=item.get("title", ""),
#                     price=item.get("price"),
#                     purchase_link=item.get("link", ""),
#                     source=item.get("source"),
#                     description=None
#                 )
#             )
#
#         all_results.append(
#             SearchOutput(
#                 query=product,
#                 products=products
#             ).model_dump()
#         )
#
#     state["search_results"] = all_results
#
#     return state


def exceuter_node(state: AgentState) -> AgentState:

    structured_executer = model.with_structured_output(ExecuterOutput)

    response = structured_executer.invoke([

        SystemMessage(content=EXECUTE_AGENT_PROMPT),
        HumanMessage(
            content=f"""
                User Request:
                {state["user_message"]}

                Search Results:
                {state["search_results"]}

                Instructions:
                 - Recommend at least one product for each requested item if available.
                 - Use only the products in the shopping results.
                 - Do not invent products.
                 - Explain why each recommendation was chosen.
                 - Keep the total cost within the user's budget when possible.
                 - If a requested product has no suitable match, clearly state that.
            """
        )
    ])
    state["final_answer"] = response.model_dump()

    # -----------------------------
    # Append this turn to chat history so future turns have context
    # -----------------------------
    state.setdefault("chat_history", [])
    state["chat_history"].append({"role": "user", "content": state["user_message"]})
    state["chat_history"].append({"role": "assistant", "content": state["final_answer"]["summary"]})

    return state


# _____________________ Define the langgraph workflow ____________________


workflow = StateGraph(AgentState)


workflow.add_node("planner", planner_node)
workflow.add_node("search", search_node)
workflow.add_node("executer", exceuter_node)


workflow.add_edge(START, "planner")
workflow.add_edge("planner", "search")
workflow.add_edge("search", "executer")
workflow.add_edge("executer", END)


# _____________________ Async main loop with Postgres memory ____________________

async def main():
    async with AsyncConnectionPool(
        conninfo=postgres_url,
        max_size=20,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    ) as pool:

        checkpointer = AsyncPostgresSaver(pool)

        # Only needs to run once ever (or once per fresh DB) — creates checkpoint tables.
        # Safe to call every startup: uses CREATE TABLE IF NOT EXISTS internally.
        await checkpointer.setup()

        graph = workflow.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "test-run-001"}}

        # One-shot example run (replace with a loop for real multi-turn use)
        initial_state = {
            "user_message": (
        "I'm setting up a home office and home gym. I need: "
        "a mechanical keyboard, a 27-inch 4K monitor, and a webcam for work; "
        "a yoga mat and a pair of adjustable dumbbells for exercise; "
        "and a standing desk. "
        "My total budget is $2500."
    ),
            "chat_history": [],
            "planner": None,
            "search_results": [],
            "final_answer": None,
        }

        result = await graph.ainvoke(initial_state, config=config)
        print(result["final_answer"])

        # Example of a true multi-turn interactive loop using the same thread_id:
        #
        # while True:
        #     user_input = input("You: ")
        #     if user_input.lower() in ("quit", "exit"):
        #         break
        #
        #     state = await graph.ainvoke({
        #         "user_message": user_input,
        #         "chat_history": [],
        #         "planner": None,
        #         "search_results": [],
        #         "final_answer": None,
        #     }, config=config)
        #
        #     print(state["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())