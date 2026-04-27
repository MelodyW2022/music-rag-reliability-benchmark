from dataclasses import dataclass
from typing import List

from .retriever import RetrievalResult


@dataclass(frozen=True)
class RecommendationExplanation:
    """
    Human-readable explanation for one retrieved recommendation.
    """

    track_name: str
    artist_name: str
    genre: str
    score: float
    explanation: str
    evidence: List[str]


def explain_recommendation(result: RetrievalResult) -> RecommendationExplanation:
    """
    Generate a grounded explanation for one retrieval result.

    The explanation only uses retrieved track fields and retriever evidence.
    """
    track = result.track
    evidence_summary = _summarize_evidence(result.evidence)
    vibe_summary = _format_vibe_tags(track.vibe_tags)

    explanation = (
        f"{track.track_name} by {track.artist_name} is recommended because "
        f"its measured audio features are close to the requested profile. "
        f"{evidence_summary} "
        f"Derived vibe tags for readability: {vibe_summary}."
    )

    return RecommendationExplanation(
        track_name=track.track_name,
        artist_name=track.artist_name,
        genre=track.genre,
        score=result.score,
        explanation=explanation,
        evidence=result.evidence,
    )


def explain_recommendations(
    results: List[RetrievalResult],
) -> List[RecommendationExplanation]:
    """
    Generate grounded explanations for a ranked list of retrieval results.
    """
    return [explain_recommendation(result) for result in results]


def _summarize_evidence(evidence: List[str]) -> str:
    """
    Convert retriever evidence into one compact explanation sentence.
    """
    score_evidence = [
        item
        for item in evidence
        if not item.startswith("derived vibe tags for explanation:")
    ]

    if not score_evidence:
        return "The retriever did not provide detailed scoring evidence."

    return " ".join(score_evidence)


def _format_vibe_tags(vibe_tags: List[str]) -> str:
    """
    Format derived vibe tags for display.
    """
    if not vibe_tags:
        return "none"

    return ", ".join(vibe_tags)
