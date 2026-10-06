from .claims import extract_claims
from .models import Analysis, Claim, ClaimResult
from .sources import SourceProvider


def analyze_text(text: str, provider: SourceProvider) -> Analysis:
    results = [_analyze_claim(claim, provider) for claim in extract_claims(text)]
    return Analysis(results=results)


def _analyze_claim(claim: Claim, provider: SourceProvider) -> ClaimResult:
    sources = provider.search(claim)
    if not sources:
        return ClaimResult(
            claim=claim,
            verdict="non vérifiable",
            confidence=0.0,
            explanation="Aucune source n'a été fournie au prototype.",
        )
    return ClaimResult(
        claim=claim,
        verdict="à examiner",
        confidence=0.25,
        explanation=(
            "Des sources candidates sont disponibles, mais le prototype ne "
            "déduit pas encore automatiquement la véracité."
        ),
        sources=sources,
    )

