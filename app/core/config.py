import os
from dotenv import load_dotenv




load_dotenv()

llm_api_key = os.getenv("GROQ_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
postgres_url = os.getenv("POSTGRES_URL")
serper_api_key=os.getenv("SERPAPI_API_KEY")


os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Agentic-AI-Proj")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
print("Tracing:", os.environ["LANGCHAIN_TRACING_V2"])
print("Project:", os.environ["LANGCHAIN_PROJECT"])


API_KEY = os.getenv("API_KEY")

SECRET_KEY=os.getenv("SECRET_KEY" , "change-me-in-production-please")
if not SECRET_KEY :
    raise RuntimeError("SECRET_KEY environment variable is not set. Please set it in your .env file or environment.")




ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))



# Basic rate limiting: max requests per IP within the time window below.
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
