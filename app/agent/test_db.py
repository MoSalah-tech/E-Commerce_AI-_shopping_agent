import psycopg, os
from dotenv import load_dotenv
print("CWD:", os.getcwd())
loaded =load_dotenv()
print("load_dotenv found a file:", loaded)
conn = psycopg.connect(os.getenv("POSTGRES_URL"))
print("Connected!")