import pytest

from src.explainer import RecommendationExplanation
from src.guardrails import (
    calculate_global_evidence_coverage,
    check_explanation,
    check_explanations,
    count_matched_evidence_markers,
    find_missing_evidence_markers,
    find_unsupported_terms,
)


def make_explanation(
    explanation_text: str = "Strong Match is grounded in genre and audio-feature similarity.",
    evidence: list[str] | None = None,
) -> RecommendationExplanation:
    if evidence is None:
        evidence = [
            "genre matches preferred genre 'pop' (+2.00)",
            "energy closeness: 0.82 vs target 0.80 (+1.96)",
            "acousticness closeness: 0.18 vs target 0.20 (+0.98)",
            "valence closeness: 0.76 vs target 0.75 (+0.99)",
            "danceability closeness: 0.81 vs target 0.80 (+0.74)",
            "derived vibe tags for explanation: high_energy, positive, danceable",
        ]

    return RecommendationExplanation(
        track_name="Strong Match",
        artist_name="Test Artist",
        genre="pop",
        score=6.50,
        explanation=explanation_text,
        evidence=evidence,
    )


def test_check_explanation_passes_grounded_output():
    report = check_explanation(make_explanation())

    assert report.passed is True
    assert report.violations == []
    assert report.unsupported_terms == []
    assert report.evidence_count == 6
    assert report.matched_evidence_markers == 5
    assert report.total_evidence_markers == 5
    assert report.fallback_explanation is None


def test_check_explanation_flags_unsupported_claims_and_builds_fallback():
    explanation = make_explanation(
        "Strong Match has emotional lyrics, rich vocals, and is a fan favorite."
    )

    report = check_explanation(explanation)

    assert report.passed is False
    assert report.unsupported_terms == ["lyrics", "vocals", "fan favorite"]
    assert [violation.code for violation in report.violations] == [
        "unsupported_claim"
    ]
    assert report.fallback_explanation is not None
    assert "Strong Match by Test Artist was retrieved with a score of 6.50" in (
        report.fallback_explanation
    )


def test_check_explanation_flags_empty_text():
    report = check_explanation(make_explanation(explanation_text="   "))

    assert report.passed is False
    assert [violation.code for violation in report.violations] == [
        "empty_explanation"
    ]
    assert report.fallback_explanation is not None


def test_check_explanation_flags_missing_evidence_as_error():
    report = check_explanation(make_explanation(evidence=[]))

    assert report.passed is False
    assert [violation.code for violation in report.violations] == [
        "missing_evidence"
    ]
    assert report.evidence_count == 0
    assert report.matched_evidence_markers == 0
    assert report.fallback_explanation is not None


def test_check_explanation_flags_incomplete_evidence_as_warning_without_fallback():
    report = check_explanation(
        make_explanation(
            evidence=[
                "genre matches preferred genre 'pop' (+2.00)",
                "energy closeness: 0.82 vs target 0.80 (+1.96)",
            ]
        )
    )

    assert report.passed is False
    assert [violation.code for violation in report.violations] == [
        "incomplete_evidence"
    ]
    assert report.violations[0].severity == "warning"
    assert report.matched_evidence_markers == 2
    assert report.fallback_explanation is None


def test_find_unsupported_terms_matches_words_and_phrases():
    terms = find_unsupported_terms(
        "The model called it chart-topping because of vocals and live performance."
    )

    assert terms == ["vocals", "chart-topping", "live performance"]
    assert find_unsupported_terms("This has a lyrical mood.") == []


def test_find_missing_evidence_markers_returns_uncovered_fields():
    missing = find_missing_evidence_markers(
        [
            "genre matches preferred genre 'pop' (+2.00)",
            "energy closeness: 0.82 vs target 0.80 (+1.96)",
        ]
    )

    assert missing == [
        "acousticness closeness",
        "valence closeness",
        "danceability closeness",
    ]


def test_count_matched_evidence_markers_counts_expected_fields():
    evidence = [
        "genre matches preferred genre 'pop' (+2.00)",
        "energy closeness: 0.82 vs target 0.80 (+1.96)",
        "valence closeness: 0.76 vs target 0.75 (+0.99)",
    ]

    assert count_matched_evidence_markers(evidence) == 3


def test_check_explanations_handles_lists():
    reports = check_explanations([make_explanation(), make_explanation()])

    assert len(reports) == 2
    assert all(report.passed for report in reports)


def test_calculate_global_evidence_coverage_uses_matched_over_possible_counts():
    complete = check_explanation(make_explanation())
    partial = check_explanation(
        make_explanation(
            evidence=[
                "genre matches preferred genre 'pop' (+2.00)",
                "energy closeness: 0.82 vs target 0.80 (+1.96)",
            ]
        )
    )

    coverage = calculate_global_evidence_coverage([complete, partial])

    assert coverage == pytest.approx(7 / 10)


def test_calculate_global_evidence_coverage_handles_empty_reports():
    assert calculate_global_evidence_coverage([]) == 0.0
