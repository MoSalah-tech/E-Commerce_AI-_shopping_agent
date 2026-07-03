from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

api_key=os.getenv("GROQ_API_KEY")




from langchain.chat_models import init_chat_model

model = init_chat_model(
    "groq:groq/compound",
    temperature=0.5,
   
)


SINGLE_AGENT_SYSTEM = """You are a helpful AI.
Task: Provide a well-reasoned recommendation to the user question.
Rules:
- Make your best effort without browsing the web.
- Be structured: Summary, Pros, Cons, Recommendation, Risks, Confidence (0-100).
"""

def single_agent_answer(question: str) -> str:
    msgs = [
        SystemMessage(content=SINGLE_AGENT_SYSTEM),
        HumanMessage(content=question),
    ]
    return model.invoke(msgs).content

question = "Should a startup use open-source LLMs or closed models in 2026? Consider cost, speed, privacy, and reliability."
print(single_agent_answer(question))
