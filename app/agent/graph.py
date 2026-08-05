import time
from urllib.parse import urlparse
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from app.core.config import *
from app.agent.state import AgentState
from app.agent.models import Planner, Product, SearchOutput, ExecuterOutput
from app.agent.prompts import PLANNER_AGENT_PROMPT, EXECUTE_AGENT_PROMPT
from app.tools.Serpapi import SerperClient
from app.agent.budget import verify_and_annotate_budget, parse_amount

# Major Egyptian e-commerce retailers -- Google's shopping/merchant-feed index
# has very sparse coverage for Egypt, but these sites ARE well indexed in
# regular Google search, so we fall back to a site-filtered organic search
# when the shopping endpoint returns nothing.
EGYPT_RETAILERS = [
    "noon.com/egypt-en",
    "jumia.com.eg",
    "btech.com",
    "2b.com.eg",
    "amazon.eg",
]


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


def _site_filtered_search_with_retry(query: str, num: int, max_attempts: int = 3):
    """Same retry pattern as shopping, but against the regular /search endpoint
    with retailer site: filters -- used as a fallback when Google's shopping
    index has nothing for the region (common for Egypt)."""
    site_filter = " OR ".join(f"site:{domain}" for domain in EGYPT_RETAILERS)
    filtered_query = f"{query} ({site_filter})"

    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return serper_client.search(query=filtered_query, num=num)
        except Exception as e:
            last_error = e
            print(f"[search_node] fallback attempt {attempt}/{max_attempts} failed for '{query}': {e}")
            if attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))
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

    MAX_HISTORY_MESSAGES = 10
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
    return {"planner": plan_obj.model_dump()}


# _________________________ Search Node ____________________________

def search_node(state: AgentState) -> AgentState:
    planner = state["planner"]

    all_results = []

    for product_name in planner["product_name"]:
        products = []

        # 1. Try Google Shopping first -- fast path, works when it has data.
        try:
            raw = _shopping_with_retry(query=product_name, num=2)
            shopping_results = raw.get("shopping", [])[:2]
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
        except Exception as e:
            print(f"[search_node] shopping search failed for '{product_name}': {e}")

        # 2. Fall back to site-filtered organic search on Egyptian retailers
        # if shopping came back empty.
        if not products:
            try:
                raw = _site_filtered_search_with_retry(query=product_name, num=6)
                organic_results = raw.get("organic", [])[:4]
                for item in organic_results:
                    link = item.get("link", "")
                    domain = urlparse(link).netloc.replace("www.", "") if link else None
                    products.append(
                        Product(
                            name=item.get("title", ""),
                            price=None,
                            purchase_link=link,
                            source=domain,
                            description=item.get("snippet"),
                        )
                    )
            except Exception as e:
                print(f"[search_node] fallback search failed for '{product_name}': {e}")

        all_results.append(
            SearchOutput(query=product_name, products=products).model_dump()
        )

    state["search_results"] = all_results
    print("[search_node] search_results:", all_results)

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
                 - Some products may not have a listed price (price is null) --
                   if the description/snippet mentions a price, use that;
                   otherwise state that the price wasn't listed and the user
                   should check the link.
                 - Explain why each recommendation was chosen.
                 - Keep the total cost within the user's budget when possible.
                 - If a requested product has no suitable match, clearly state that.
            """
        )
    ])
    final_answer = response.model_dump()

    planner = state.get("planner") or {}
    final_answer = verify_and_annotate_budget(final_answer, planner.get("budget"))
    return {
        "final_answer": final_answer,
        "chat_history": [
            {"role": "user", "content": state["user_message"]},
            {
                "role": "assistant",
                "content": final_answer["summary"],
                "recommendations": final_answer.get("recommendation", []),
            },
        ],
    }


workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("search", search_node)
workflow.add_node("executer", exceuter_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "search")
workflow.add_edge("search", "executer")
workflow.add_edge("executer", END)