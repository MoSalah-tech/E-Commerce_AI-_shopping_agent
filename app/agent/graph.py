import time
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from app.core.config import *
from app.agent.state import AgentState
from app.agent.models import Planner, Product, SearchOutput, ExecuterOutput
from app.agent.prompts import PLANNER_AGENT_PROMPT,  EXECUTE_AGENT_PROMPT
from app.tools.Serpapi import SerperClient
from app.agent.budget import verify_and_annotate_budget,parse_amount



def _shopping_with_retry(query: str, num: int, max_attempts: int = 3):
    """Retries a transient Serper failure (timeout, momentary network/rate-limit
    blip) with a short backoff before giving up — a single bad moment
    shouldn't turn into a permanent "no products found" for the user."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return serper_client.shopping(query=query, num=num)
        except Exception as e:
            last_error = e
            print(f"[search_node] attempt {attempt}/{max_attempts} failed for '{query}': {e}")
            if attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))  # 1s, 2s, 4s...
    raise last_error


serper_client = SerperClient()


model = ChatGroq(
    api_key=llm_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)


# ___________________________ Planner Node ______________________
def planner_node(state: AgentState) -> AgentState:
    structured_planner = model.with_structured_output(Planner)

    # Only send the most recent turns to the LLM — sending the FULL history on
    # every call means token usage (and cost/latency) grows without bound as a
    # conversation gets longer, and eventually blows past Groq's TPM limit.
    MAX_HISTORY_MESSAGES = 10  # ~5 user/assistant turns
    recent_history = state.get("chat_history", [])[-MAX_HISTORY_MESSAGES:]

    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in recent_history
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
    # Return ONLY the keys this node actually changed. Returning the whole
    # `state` dict here would re-include chat_history unchanged, and because
    # chat_history uses an operator.add reducer, that would double it on
    # every single node — not just once per turn, but once per NODE per turn.
    return {"planner": plan_obj.model_dump()}


# _________________________ Search Node using Serper.dev (Shopping API) ____________________________

# Serper's shopping endpoint already returns structured product data (title, price,
# link, source) directly, so no LLM structuring pass is needed here.

def search_node(state: AgentState) -> AgentState:
    planner = state["planner"]

    all_results = []

    for product_name in planner["product_name"]:

        try:
            raw = _shopping_with_retry(query=product_name, num=2)
        except Exception as e:
            # Don't let one failed product search take down the whole graph run,
            # but DO surface what actually went wrong.
            print(f"[search_node] Serper request failed for '{product_name}': {e}")
            all_results.append(
                SearchOutput(query=product_name, products=[]).model_dump()
            )
            continue

        # Hard cap client-side — some APIs treat `num` as a soft hint rather
        # than a strict limit, so we truncate here to guarantee exactly 2.
        shopping_results = raw.get("shopping", [])[:2]

        products = []
        for item in shopping_results:
            products.append(
                Product(
                    name=item.get("title", ""),
                    price=item.get("price"),
                    purchase_link=item.get("link"),
                    source=item.get("source"),
                    description=None,
                )
            )

        all_results.append(
            SearchOutput(
                query=product_name,
                products=products,
            ).model_dump()
        )

    state["search_results"] = all_results
    print("[search_node] search_results:", all_results)

    # Return ONLY the key this node changed — see note in planner_node about
    # why returning the whole state dict corrupts the chat_history reducer.
    return {"search_results": all_results}


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
    final_answer = response.model_dump()

    # The LLM's own claim about whether recommendations fit the budget can be
    # wrong (observed in testing: it once said a lower price "exceeded" a
    # higher budget). Recompute the real total in Python and append a
    # ground-truth verified note, rather than trusting the LLM's arithmetic.
    planner = state.get("planner") or {}
    final_answer = verify_and_annotate_budget(final_answer, planner.get("budget"))
    return {
        "final_answer": final_answer,
        "chat_history": [
            {"role": "user", "content": state["user_message"]},
            {"role": "assistant", "content": final_answer["summary"]},
        ],
    }


# _____________________ Define the langgraph workflow ____________________


workflow = StateGraph(AgentState)


workflow.add_node("planner", planner_node)
workflow.add_node("search", search_node)
workflow.add_node("executer", exceuter_node)


workflow.add_edge(START, "planner")
workflow.add_edge("planner", "search")
workflow.add_edge("search", "executer")
workflow.add_edge("executer", END)
