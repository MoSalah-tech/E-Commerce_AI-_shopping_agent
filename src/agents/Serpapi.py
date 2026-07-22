# import os 
# from dotenv import load_dotenv
# from serpapi import GoogleSearch

# load_dotenv()

# __________________________SerpAPI search______________________
from __future__ import annotations

from typing import Any, Dict, Optional
import requests


class SerperClient:
    BASE_URL = "https://google.serper.dev"

    def __init__(
        self,
        api_key: str,
        gl: str = "eg",
        timeout: int = 30,
    ) -> None:
        self.gl = gl
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            }
        )

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.BASE_URL}/{endpoint}",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json()

    def shopping(
        self,
        query: str,
        num: int = 10,
        gl: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "q": query,
            "gl": gl or self.gl,
            "num": num,
        }
        return self._post("shopping", payload)


if __name__ == "__main__":
    client = SerperClient(api_key="fa7045fa906b84244f230518f29e1fd8fdf9f905")

    result = client.shopping(
        query="iPhone 16 Pro",
        num=40,
    )

    print(result)