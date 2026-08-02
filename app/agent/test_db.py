# test_connection.py
import asyncio
import sys
import psycopg

# Must be set before asyncio.run() on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

POSTGRES_URL = "postgresql://postgres.oxlyujwpuwrjqwlnvzit:mosalah8899@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

async def test():
    try:
        async with await psycopg.AsyncConnection.connect(POSTGRES_URL) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT version();")
                result = await cur.fetchone()
                print("✅ Connected successfully!")
                print(result[0])
    except Exception as e:
        print("❌ Connection failed:")
        print(e)

asyncio.run(test())