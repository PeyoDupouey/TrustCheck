import re

from .models import Claim


_FACTUAL_MARKERS = re.compile(
    r"\b(est|sont|a|ont|serait|seraient|causes?|provoque|provoquent|"
    r"million|milliard|pour ?cent|%|en \d{4}|selon)\b",
    re.IGNORECASE,
)


def extract_claims(text: str) -> list[Claim]:
    """Extrait des phrases candidates sans prétendre déterminer leur vérité.

    Cette heuristique est volontairement remplaçable par un modèle local ou un
    LLM lors d'une étape ultérieure.
    """
    claims: list[Claim] = []
    for position, sentence in enumerate(re.split(r"(?<=[.!?])\s+", text.strip())):
        sentence = sentence.strip()
        if sentence and _FACTUAL_MARKERS.search(sentence):
            claims.append(Claim(text=sentence, position=position))
    return claims

