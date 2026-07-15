import os 
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

# __________________________SerpAPI search______________________
serp_api = os.getenv("SERPAPI_API_KEY")



def shopping_search(query: str):

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key":serp_api,
        "num": 5,
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    return results.get("shopping_results", [])
