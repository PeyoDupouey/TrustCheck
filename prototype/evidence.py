"""Indice explicable de couverture des sources, sans LLM."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import Claim, Source


_WORD = re.compile(r"[\wÀ-ÿ]{3,}", re.UNICODE)
_STOP_WORDS = {
    "avec", "aussi", "aux", "cette", "comme", "dans", "des", "dont", "elle", "elles",
    "entre", "être", "leurs", "mais", "même", "nous", "pour", "plus", "sans", "sont",
    "sur", "une", "vous", "will", "with", "from", "that", "this", "the", "and",
}
_INSTITUTIONAL_SUFFIXES = (".gouv.fr", ".gov", ".int", ".europa.eu", ".edu")
_INSTITUTIONAL_DOMAINS = {"who.int", "un.org", "worldbank.org", "oecd.org", "insee.fr"}


def _terms(text: str) -> set[str]:
    return {word.casefold() for word in _WORD.findall(text) if word.casefold() not in _STOP_WORDS}


def _domain(url: str) -> str:
    return urlparse(url).netloc.casefold().removeprefix("www.")


def evidence_score(claim: Claim, sources: list[Source]) -> tuple[float, list[Source]]:
    """Retourne un indice de couverture des preuves candidates (0 à 1).

    L'indice mesure la correspondance observable entre l'affirmation et les
    extraits, pas la véracité de l'affirmation. Il est volontairement plafonné
    sous 80 % car aucun raisonnement sémantique n'est effectué ici.
    """

    claim_terms = _terms(claim.text)
    scored: list[tuple[float, Source]] = []
    for source in sources:
        source_terms = _terms(f"{source.title} {source.excerpt}")
        overlap = len(claim_terms & source_terms) / max(1, len(claim_terms))
        scored.append((overlap, source))
    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [source for _, source in scored[:3]]
    if not selected:
        return 0.0, []

    average_overlap = sum(score for score, _ in scored[:3]) / len(selected)
    domains = {_domain(source.url) for source in selected}
    diversity = min(1.0, len(domains) / 3)
    institutional = any(
        domain.endswith(_INSTITUTIONAL_SUFFIXES) or domain in _INSTITUTIONAL_DOMAINS
        for domain in domains
    )
    score = 0.18 + (0.45 * average_overlap) + (0.12 * diversity) + (0.12 if institutional else 0.0)
    return min(0.78, round(score, 2)), selected
