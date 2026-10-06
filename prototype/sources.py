from collections.abc import Iterable
from typing import Protocol

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

