import json
from collections.abc import Iterable
from urllib.request import Request, urlopen

from .models import Claim, Source


VERDICT_VALUES = [
    "confirmée",
    "probablement confirmée",
    "contestée",
    "probablement fausse",
    "fausse",
    "non vérifiable",
    "sources contradictoires",
]


class OllamaFactChecker:
    """Client minimal de l'API Ollama locale avec sortie JSON structurée."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:3b", timeout: float = 300.0, max_sources: int = 5) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_sources = max_sources

    def judge(self, claim: Claim, sources: Iterable[Source]) -> dict:
        source_list = list(sources)[: self.max_sources]
        evidence = "\n\n".join(
            f"[{index}] {source.title}\nURL: {source.url}\nExtrait: {source.excerpt[:600]}"
            for index, source in enumerate(source_list, start=1)
        )
        schema = {
            "type": "object",
            "properties": {
                "verdict": {"type": "string", "enum": VERDICT_VALUES},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "explanation": {"type": "string"},
                "source_urls": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["verdict", "confidence", "explanation", "source_urls"],
        }
        prompt = (
            "Tu es un assistant de vérification factuelle. Analyse uniquement "
            "l'affirmation avec les sources fournies. Ne déduis pas une vérité "
            "sans preuve. Si les sources sont insuffisantes, utilise non vérifiable.\n\n"
            f"AFFIRMATION:\n{claim.text}\n\nSOURCES:\n{evidence}\n\n"
            "Réponds uniquement avec le JSON demandé."
        )
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": schema,
            "options": {"temperature": 0, "num_predict": 256},
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        result = json.loads(payload.get("message", {}).get("content", ""))
        if result.get("verdict") not in VERDICT_VALUES:
            raise ValueError("Verdict Ollama invalide")
        result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))
        result["source_urls"] = [url for url in result.get("source_urls", []) if isinstance(url, str)]
        return result
