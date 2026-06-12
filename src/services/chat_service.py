# -*- coding: utf-8 -*-
"""DeepSeek chat service."""
import os
from pathlib import Path
from typing import Dict, List

import requests


class ChatService:
    """Small OpenAI-compatible client for DeepSeek."""

    DEFAULT_ENDPOINT = "https://api.deepseek.com/chat/completions"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self):
        self._load_env_file()
        self.api_key = (
            os.getenv("DEEPSEEK_API_KEY")
            or os.getenv("AI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        ).strip()
        self.endpoint = os.getenv("DEEPSEEK_API_URL", self.DEFAULT_ENDPOINT).strip()
        self.model = os.getenv("DEEPSEEK_MODEL", self.DEFAULT_MODEL).strip()

    def _load_env_file(self):
        """Load local env values without adding a dependency."""
        root = Path(__file__).resolve().parents[2]
        for name in (".env.local", ".env"):
            path = root / name
            if not path.exists():
                continue
            for raw_line in path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def send(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            raise RuntimeError(
                "Chưa có DEEPSEEK_API_KEY hoặc AI_API_KEY. Hãy thêm key vào biến môi trường hoặc file .env.local."
            )

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
            },
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
