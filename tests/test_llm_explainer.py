import pytest

from src.data_loader import TrackRecord
import src.llm_explainer as llm_explainer
from src.llm_explainer import (
    build_gemini_prompt,
    explain_with_gemini,
    parse_gemini_explanation,
)
from src.retriever import RetrievalResult


@pytest.fixture
def retrieval_result() -> RetrievalResult:
    track = TrackRecord(
        track_name="Strong Match",
        artist_name="Test Artist",
        album_name="Test Album",
        genre="pop",
        vibe_tags=["high_energy", "positive", "danceable"],
        popularity=50.0,
        danceability=0.81,
        energy=0.82,
        acousticness=0.18,
        valence=0.76,
        tempo=120.0,
    )

    return RetrievalResult(
        track=track,
        score=6.50,
        evidence=[
            "genre matches preferred genre 'pop' (+2.00)",
            "energy closeness: 0.82 vs target 0.80 (+1.96)",
            "acousticness closeness: 0.18 vs target 0.20 (+0.98)",
            "valence closeness: 0.76 vs target 0.75 (+0.99)",
            "danceability closeness: 0.81 vs target 0.80 (+0.74)",
            "derived vibe tags for explanation: high_energy, positive, danceable",
        ],
    )


def test_build_gemini_prompt_uses_retrieved_fields_and_guardrails(
    retrieval_result: RetrievalResult,
):
    prompt = build_gemini_prompt(retrieval_result)

    assert "Use only the provided track metadata and retrieval evidence." in prompt
    assert "Return only valid JSON" in prompt
    assert "- name: Strong Match" in prompt
    assert "- artist: Test Artist" in prompt
    assert "- retrieval_score: 6.50" in prompt
    assert "- derived_vibe_tags: high_energy, positive, danceable" in prompt
    assert "- energy closeness: 0.82 vs target 0.80 (+1.96)" in prompt
    assert "Do not mention lyrics, vocals, storytelling" in prompt


def test_parse_gemini_explanation_accepts_plain_json():
    explanation = parse_gemini_explanation(
        '{"explanation": "This track matches the requested energy and genre."}'
    )

    assert explanation == "This track matches the requested energy and genre."


def test_parse_gemini_explanation_accepts_json_code_fence():
    explanation = parse_gemini_explanation(
        '```json\n{"explanation": "This track is grounded in retrieved evidence."}\n```'
    )

    assert explanation == "This track is grounded in retrieved evidence."


def test_parse_gemini_explanation_rejects_malformed_output():
    assert parse_gemini_explanation("This is not JSON.") is None
    assert parse_gemini_explanation('{"text": "missing explanation key"}') is None
    assert parse_gemini_explanation('{"explanation": "   "}') is None


def test_explain_with_gemini_uses_deterministic_fallback_without_key(
    monkeypatch: pytest.MonkeyPatch,
    retrieval_result: RetrievalResult,
):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = explain_with_gemini(retrieval_result)

    assert result.used_llm is False
    assert result.raw_response is None
    assert result.fallback_reason == "missing Gemini API key"
    assert result.guardrail_report is None
    assert result.explanation.track_name == "Strong Match"
    assert result.explanation.evidence == retrieval_result.evidence
    assert "Strong Match by Test Artist" in result.explanation.explanation


def test_explain_with_gemini_returns_safe_guardrail_checked_output(
    monkeypatch: pytest.MonkeyPatch,
    retrieval_result: RetrievalResult,
):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_explainer,
        "_generate_gemini_response_text",
        lambda result, model: (
            '{"explanation": "Strong Match by Test Artist matches the request '
            'using retrieved genre and audio-feature evidence."}'
        ),
    )

    result = explain_with_gemini(retrieval_result)

    assert result.used_llm is True
    assert result.raw_response is not None
    assert result.fallback_reason is None
    assert result.guardrail_report is not None
    assert result.guardrail_report.passed is True
    assert result.explanation.explanation == (
        "Strong Match by Test Artist matches the request using retrieved genre "
        "and audio-feature evidence."
    )
    assert result.explanation.evidence == retrieval_result.evidence


def test_explain_with_gemini_falls_back_when_guardrails_fail(
    monkeypatch: pytest.MonkeyPatch,
    retrieval_result: RetrievalResult,
):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_explainer,
        "_generate_gemini_response_text",
        lambda result, model: (
            '{"explanation": "Strong Match has emotional lyrics and rich vocals."}'
        ),
    )

    result = explain_with_gemini(retrieval_result)

    assert result.used_llm is False
    assert result.raw_response is not None
    assert result.fallback_reason == "Gemini explanation failed guardrails"
    assert result.guardrail_report is not None
    assert result.guardrail_report.passed is False
    assert result.guardrail_report.unsupported_terms == ["lyrics", "vocals"]
    assert result.explanation.track_name == "Strong Match"
    assert "Strong Match by Test Artist" in result.explanation.explanation
