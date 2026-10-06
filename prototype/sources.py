import json
from collections.abc import Iterable
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def search(self, claim: Claim) -> list[Source]:
        query = urlencode({"q": claim.text, "format": "json", "language": "fr"})
        request = Request(
            f"{self.base_url}/search?{query}",
            headers={"Accept": "application/json", "User-Agent": "TrustCheck/0.1"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        return [
            Source(
                title=item.get("title", "Source sans titre"),
                url=item["url"],
                excerpt=item.get("content", ""),
                published_at=item.get("publishedDate"),
            )
            for item in payload.get("results", [])
            if item.get("url")
        ]
