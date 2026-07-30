from __future__ import annotations

import os
from typing import Any, Dict, Optional
import requests


class SerperClient:
    BASE_URL = "https://google.serper.dev"

    def __init__(
        self,
        api_key: Optional[str] = None,
        gl: str = "eg",
        timeout: int = 30,
    ) -> None:
        # Falls back to SERPER_API_KEY from .env if not passed explicitly
        resolved_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "No Serper API key provided. Set SERPER_API_KEY in your .env "
                "or pass api_key explicitly."
            )

        self.gl = gl
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": resolved_key,
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
        num: int,
        gl: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "q": query,
            "gl": gl or self.gl,
            "num": num,
        }
        return self._post("shopping", payload)