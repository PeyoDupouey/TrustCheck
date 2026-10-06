from .claims import extract_claims
from .models import Analysis, Claim, ClaimResult
from .sources import SourceProvider


def analyze_text(text: str, provider: SourceProvider, judge=None) -> Analysis:
    results = [_analyze_claim(claim, provider, judge) for claim in extract_claims(text)]
    return Analysis(results=results)


def _analyze_claim(claim: Claim, provider: SourceProvider, judge=None) -> ClaimResult:
    sources = provider.search(claim)
    if not sources:
        return ClaimResult(
            claim=claim,
            verdict="non vérifiable",
            confidence=0.0,
            explanation="Aucune source n'a été fournie au prototype.",
        )
    if judge is not None:
        try:
            judged = judge.judge(claim, sources)
        except (OSError, TimeoutError, ValueError) as error:
            return ClaimResult(
                claim=claim,
                verdict="non vérifiable",
                confidence=0.0,
                explanation=f"La réponse du LLM n'est pas exploitable : {error}.",
                sources=sources,
            )
        selected_sources = [source for source in sources if source.url in judged["source_urls"]]
        return ClaimResult(
            claim=claim,
            verdict=judged["verdict"],
            confidence=judged["confidence"],
            explanation=judged["explanation"],
            sources=selected_sources,
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
