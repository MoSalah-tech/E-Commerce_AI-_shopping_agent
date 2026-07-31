from typing import Any, Dict

from app.core.lifespan import get_graph

async def run_agent(thread_id: str, user_message: str) -> Dict[str, Any]:
    try:
        graph = get_graph()
    except RuntimeError as e:
        return {"success": False, "error": str(e)}

    config = {"configurable": {"thread_id": thread_id}}

    input_state = {
        "user_message": user_message,
        "chat_history": [],
        "planner": None,
        "search_results": [],
        "final_answer": None,
    }

    try:
        result = await graph.ainvoke(input_state, config=config)
    except Exception as e:
        # Catches: Groq schema validation errors, Serper/network failures,
        # Postgres connection issues, or anything else unexpected from the
        # graph run. The caller (route handler) gets a clean error instead
        # of a raw traceback / 500 with no context.
        print(f"[run_agent] graph run failed for thread '{thread_id}': {e}")
        return {
            "success": False,
            "error": "Something went wrong while processing your request. Please try again.",
        }

    final_answer = result.get("final_answer")
    if final_answer is None:
        print(f"[run_agent] graph completed but final_answer was None for thread '{thread_id}'")
        return {
            "success": False,
            "error": "No recommendation could be generated. Please try rephrasing your request.",
        }

    return {
        "success": True,
        "data": final_answer,
    }
