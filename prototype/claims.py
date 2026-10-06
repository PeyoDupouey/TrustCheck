import re

from .models import Claim


_FACTUAL_MARKERS = re.compile(
    r"\b(est|sont|a|ont|serait|seraient|causes?|provoque|provoquent|"
    r"million|milliard|pour ?cent|%|en \d{4}|selon)\b",
    re.IGNORECASE,
)
_NUMERIC_MARKERS = re.compile(r"\b\d+(?:[\s.,]\d+)*\b|%|€|\$|\b(en|depuis|avant)\s+\d{4}\b", re.IGNORECASE)
_SUBJECTIVE_MARKERS = re.compile(
    r"\b(je pense|je trouve|j['’]aime|j['’]adore|à mon avis|incroyable|magnifique|nul|super)\b",
    re.IGNORECASE,
)


def _checkworthiness(sentence: str) -> float:
    """Priorise les phrases qui contiennent des éléments vérifiables."""

    score = 0.15
    if _FACTUAL_MARKERS.search(sentence):
        score += 0.35
    if _NUMERIC_MARKERS.search(sentence):
        score += 0.30
    if len(sentence.split()) >= 8:
        score += 0.10
    if _SUBJECTIVE_MARKERS.search(sentence):
        score -= 0.55
    return max(0.0, min(1.0, round(score, 2)))


def extract_claims(text: str) -> list[Claim]:
    """Extrait des phrases candidates sans prétendre déterminer leur vérité.

    Cette heuristique est volontairement remplaçable par un modèle local ou un
    LLM lors d'une étape ultérieure.
    """
    claims: list[Claim] = []
    for position, sentence in enumerate(re.split(r"(?<=[.!?])\s+", text.strip())):
        sentence = sentence.strip()
        score = _checkworthiness(sentence)
        if sentence and score >= 0.35:
            claims.append(Claim(text=sentence, position=position, checkworthiness=score))
    return sorted(claims, key=lambda claim: (-claim.checkworthiness, claim.position))
