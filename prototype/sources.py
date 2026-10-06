import json
from collections.abc import Iterable
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .cache import MemoryTTLCache, content_key
from .models import Claim, Source


class SourceProvider(Protocol):
    def search(self, claim: Claim) -> list[Source]: ...


class StaticSourceProvider:
    """Fournisseur déterministe utilisé par le prototype et ses tests."""

    def __init__(self, sources: Iterable[Source] = ()) -> None:
        self._sources = list(sources)

    def search(self, claim: Claim) -> list[Source]:
        del claim
        return list(self._sources)


class SearxngSourceProvider:
    """Recherche SearXNG compatible JSON, sans clé API.

    Le serveur doit être fourni par l'utilisateur, par exemple une instance
    locale. Les résultats restent des sources candidates : ils ne constituent
    pas à eux seuls une preuve de véracité.
    """

    def __init__(self, base_url: str, timeout: float = 2.0, max_results: int = 5) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_results = max_results
        self._cache: MemoryTTLCache[list[Source]] = MemoryTTLCache(ttl_seconds=600.0)

    def search(self, claim: Claim) -> list[Source]:
        cached = self._cache.get(content_key(claim.text))
        if cached is not None:
            return list(cached)
        query = urlencode({"q": claim.text, "format": "json", "language": "fr"})
        request = Request(
            f"{self.base_url}/search?{query}",
            headers={"Accept": "application/json", "User-Agent": "TrustCheck/0.1"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        sources = [
            Source(
                title=item.get("title", "Source sans titre"),
                url=item["url"],
                excerpt=item.get("content", ""),
                published_at=item.get("publishedDate"),
            )
            for item in payload.get("results", [])
            if item.get("url")
        ]
        sources = sources[: self.max_results]
        self._cache.put(content_key(claim.text), sources)
        return list(sources)
