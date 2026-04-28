from dataclasses import dataclass
import re
from typing import List, Optional

from .explainer import RecommendationExplanation


UNSUPPORTED_CLAIM_TERMS = [
    "lyrics",
    "lyric",
    "vocals",
    "vocal",
    "storytelling",
    "fan favorite",
    "critically acclaimed",
    "award-winning",
    "chart-topping",
    "live performance",
    "instrumentation",
]

REQUIRED_EVIDENCE_MARKERS = [
    "genre",
    "energy closeness",
    "acousticness closeness",
    "valence closeness",
    "danceability closeness",
]


@dataclass(frozen=True)
class GuardrailViolation:
    """
    One reliability issue found in a recommendation explanation.
    """

    code: str
    message: str
    severity: str


@dataclass(frozen=True)
class GuardrailReport:
    """
    Result of checking one recommendation explanation.
    """

    passed: bool
    violations: List[GuardrailViolation]
    unsupported_terms: List[str]
    evidence_count: int
    matched_evidence_markers: int
    total_evidence_markers: int
    fallback_explanation: Optional[str]


def check_explanation(
    explanation: RecommendationExplanation,
) -> GuardrailReport:
    """
    Check whether a generated recommendation explanation is grounded.

    This guardrail is deterministic and offline. It does not judge whether the
    recommendation is good; it checks whether the explanation stays within the
    evidence available from retrieval.
    """
    violations: List[GuardrailViolation] = []

    if not explanation.explanation.strip():
        violations.append(
            GuardrailViolation(
                code="empty_explanation",
                message="Explanation text is empty.",
                severity="error",
            )
        )

    unsupported_terms = find_unsupported_terms(explanation.explanation)
    if unsupported_terms:
        violations.append(
            GuardrailViolation(
                code="unsupported_claim",
                message=(
                    "Explanation includes claims that are not supported by "
                    f"the available track evidence: {', '.join(unsupported_terms)}."
                ),
                severity="error",
            )
        )

    if not explanation.evidence:
        violations.append(
            GuardrailViolation(
                code="missing_evidence",
                message="Explanation does not include retrieval evidence.",
                severity="error",
            )
        )

    missing_markers = find_missing_evidence_markers(explanation.evidence)
    if explanation.evidence and missing_markers:
        violations.append(
            GuardrailViolation(
                code="incomplete_evidence",
                message=(
                    "Retriever evidence is missing expected grounding fields: "
                    f"{', '.join(missing_markers)}."
                ),
                severity="warning",
            )
        )

    fallback_explanation = None
    if any(violation.severity == "error" for violation in violations):
        fallback_explanation = build_fallback_explanation(explanation)

    return GuardrailReport(
        passed=len(violations) == 0,
        violations=violations,
        unsupported_terms=unsupported_terms,
        evidence_count=len(explanation.evidence),
        matched_evidence_markers=count_matched_evidence_markers(explanation.evidence),
        total_evidence_markers=len(REQUIRED_EVIDENCE_MARKERS),
        fallback_explanation=fallback_explanation,
    )


def check_explanations(
    explanations: List[RecommendationExplanation],
) -> List[GuardrailReport]:
    """
    Check a list of recommendation explanations.
    """
    return [check_explanation(explanation) for explanation in explanations]


def find_unsupported_terms(text: str) -> List[str]:
    """
    Find terms that imply unsupported knowledge.

    These terms are blocked because the current system only has track metadata,
    audio features, retriever evidence, and derived vibe tags.
    """
    normalized_text = text.lower()

    return [
        term
        for term in UNSUPPORTED_CLAIM_TERMS
        if _contains_term(normalized_text, term)
    ]


def find_missing_evidence_markers(evidence: List[str]) -> List[str]:
    """
    Check whether expected retriever evidence fields are present.
    """
    normalized_evidence = " ".join(evidence).lower()

    return [
        marker
        for marker in REQUIRED_EVIDENCE_MARKERS
        if marker not in normalized_evidence
    ]


def count_matched_evidence_markers(evidence: List[str]) -> int:
    """
    Count how many expected retriever evidence fields are present.
    """
    normalized_evidence = " ".join(evidence).lower()

    return sum(
        1
        for marker in REQUIRED_EVIDENCE_MARKERS
        if marker in normalized_evidence
    )


def calculate_global_evidence_coverage(reports: List[GuardrailReport]) -> float:
    """
    Calculate evidence coverage across all checked explanations.
    """
    total_possible = sum(report.total_evidence_markers for report in reports)
    if total_possible == 0:
        return 0.0

    total_matched = sum(report.matched_evidence_markers for report in reports)
    return total_matched / total_possible


def build_fallback_explanation(
    explanation: RecommendationExplanation,
) -> str:
    """
    Build a safer fallback explanation when the original one fails guardrails.
    """
    return (
        f"{explanation.track_name} by {explanation.artist_name} was retrieved "
        f"with a score of {explanation.score:.2f}. This recommendation is "
        "grounded in the retrieved genre, audio-feature similarity, and any "
        "derived vibe tags shown in the evidence."
    )


def _contains_term(text: str, term: str) -> bool:
    """
    Match blocked terms as words or phrases instead of arbitrary substrings.
    """
    pattern = rf"\b{re.escape(term)}\b"
    return re.search(pattern, text) is not None
