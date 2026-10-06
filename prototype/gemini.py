"""Client Gemini optionnel pour le jugement factuel côté serveur."""

from __future__ import annotations

import json
from collections.abc import Iterable
from urllib.parse import quote
from urllib.request import Request, urlopen

from .llm import VERDICT_VALUES
from .models import Claim, Source


class GeminiFactChecker:
    """Utilise Gemini uniquement côté API locale, jamais dans l'extension."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", timeout: float = 45.0, max_sources: int = 3) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_sources = max_sources

    def judge(self, claim: Claim, sources: Iterable[Source]) -> dict:
        source_list = list(sources)[: self.max_sources]
        evidence = "\n\n".join(
            f"[{index}] {source.title}\nExtrait: {source.excerpt[:400]}"
            for index, source in enumerate(source_list, start=1)
        )
        schema = {
            "type": "OBJECT",
            "properties": {
                "verdict": {"type": "STRING", "enum": VERDICT_VALUES},
                "confidence": {"type": "NUMBER"},
                "explanation": {"type": "STRING"},
                "source_indexes": {"type": "ARRAY", "items": {"type": "INTEGER"}},
            },
            "required": ["verdict", "confidence", "explanation", "source_indexes"],
        }
        prompt = (
            "Vérifie uniquement l'affirmation avec les sources ci-dessous. "
            "N'invente rien. Si les preuves sont insuffisantes, réponds non vérifiable. "
            "Réponds en français avec une explication de 120 caractères maximum et au maximum une source.\n\n"
            f"AFFIRMATION : {claim.text}\n\nSOURCES :\n{evidence}"
        )
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{quote(self.model, safe='')}:generateContent?key={quote(self.api_key, safe='')}"
        )
        request = Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        content = payload["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(content)
        if result.get("verdict") not in VERDICT_VALUES:
            raise ValueError("Verdict Gemini invalide")
        result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))
        indexes = {
            index for index in result.get("source_indexes", [])
            if isinstance(index, int) and 1 <= index <= len(source_list)
        }
        result["source_urls"] = [source_list[index - 1].url for index in sorted(indexes)]
        return result
