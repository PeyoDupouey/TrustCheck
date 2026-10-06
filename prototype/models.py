from dataclasses import dataclass, field


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    excerpt: str = ""
    published_at: str | None = None


@dataclass(frozen=True)
class Claim:
    text: str
    position: int


@dataclass
class ClaimResult:
    claim: Claim
    verdict: str
    confidence: float
    explanation: str
    sources: list[Source] = field(default_factory=list)


@dataclass
class Analysis:
    results: list[ClaimResult]

