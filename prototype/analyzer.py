from .claims import extract_claims
from .evidence import evidence_score
from .models import Analysis, Claim, ClaimResult
from .sources import SourceProvider


def analyze_text(text: str, provider: SourceProvider, judge=None, max_claims: int = 3) -> Analysis:
    """Analyse seulement quelques affirmations du contenu visible.

    La limite évite de bloquer le défilement sur une publication contenant
    beaucoup de phrases. Une future extension pourra lancer les suivantes en
    arrière-plan si l'utilisateur reste sur la publication.
    """

    claims = extract_claims(text)[:max_claims]
    results = [_analyze_claim(claim, provider, judge) for claim in claims]
    return Analysis(results=results)


def _analyze_claim(claim: Claim, provider: SourceProvider, judge=None) -> ClaimResult:
    sources = provider.search(claim)
    if not sources:
        return ClaimResult(
            claim=claim,
            verdict="non vérifiable",
            confidence=0.0,
            explanation="Aucune source n'a été fournie au prototype.",
            confidence_kind="couverture des sources",
        )
    if judge is not None:
        try:
            judged = judge.judge(claim, sources)
        except (OSError, TimeoutError, ValueError):
            score, selected_sources = evidence_score(claim, sources)
            return ClaimResult(
                claim=claim,
                verdict="à examiner",
                confidence=score,
                explanation=(
                    "Le jugement automatique est indisponible. Le score indique "
                    "la couverture des extraits trouvés, pas la vérité de l'affirmation."
                ),
                sources=selected_sources,
                confidence_kind="couverture des sources",
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
        confidence=evidence_score(claim, sources)[0],
        explanation=(
            "Le score indique la couverture des extraits trouvés, pas la vérité "
            "de l'affirmation."
        ),
        sources=evidence_score(claim, sources)[1],
        confidence_kind="couverture des sources",
    )
