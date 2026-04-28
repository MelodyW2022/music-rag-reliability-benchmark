from dataclasses import dataclass
import json
import os
import re
from typing import Optional

from .explainer import RecommendationExplanation, explain_recommendation
from .guardrails import GuardrailReport, check_explanation
from .retriever import RetrievalResult


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


@dataclass(frozen=True)
class LLMExplanationResult:
    """
    Result of trying to generate an explanation with Gemini.

    The explanation is always populated. If Gemini is unavailable or returns
    malformed output, explanation falls back to the deterministic explainer.
    """

    explanation: RecommendationExplanation
    used_llm: bool
    raw_response: Optional[str]
    fallback_reason: Optional[str]
    guardrail_report: Optional[GuardrailReport]


def explain_with_gemini(
    result: RetrievalResult,
    model: str = DEFAULT_GEMINI_MODEL,
) -> LLMExplanationResult:
    """
    Generate a grounded recommendation explanation with Gemini when available.

    Gemini is used only as a wording layer. Retrieval remains the source of
    truth, and the deterministic explainer is used when no API key, SDK, or
    parseable response is available.
    """
    if not _has_gemini_api_key():
        return _deterministic_fallback(result, "missing Gemini API key")

    try:
        raw_response = _generate_gemini_response_text(result, model)
    except ImportError:
        return _deterministic_fallback(result, "google-genai package is not installed")
    except Exception as exc:
        return _deterministic_fallback(result, f"Gemini request failed: {exc}")

    if not raw_response:
        return _deterministic_fallback(result, "Gemini returned an empty response")

    explanation_text = parse_gemini_explanation(raw_response)
    if not explanation_text:
        fallback = explain_recommendation(result)
        return LLMExplanationResult(
            explanation=fallback,
            used_llm=False,
            raw_response=raw_response,
            fallback_reason="Gemini response did not contain a valid explanation",
            guardrail_report=None,
        )

    track = result.track
    gemini_explanation = RecommendationExplanation(
        track_name=track.track_name,
        artist_name=track.artist_name,
        genre=track.genre,
        score=result.score,
        explanation=explanation_text,
        evidence=result.evidence,
    )
    guardrail_report = check_explanation(gemini_explanation)

    if guardrail_report.fallback_explanation:
        return LLMExplanationResult(
            explanation=explain_recommendation(result),
            used_llm=False,
            raw_response=raw_response,
            fallback_reason="Gemini explanation failed guardrails",
            guardrail_report=guardrail_report,
        )

    return LLMExplanationResult(
        explanation=gemini_explanation,
        used_llm=True,
        raw_response=raw_response,
        fallback_reason=None,
        guardrail_report=guardrail_report,
    )


def build_gemini_prompt(result: RetrievalResult) -> str:
    """
    Build a strict prompt that limits Gemini to retrieved evidence only.
    """
    track = result.track
    evidence_lines = "\n".join(f"- {item}" for item in result.evidence)
    vibe_tags = ", ".join(track.vibe_tags) if track.vibe_tags else "none"

    return f"""
You are writing a grounded music recommendation explanation.

Use only the provided track metadata and retrieval evidence.
Do not mention lyrics, vocals, storytelling, live performance, reviews, awards,
chart status, fan reactions, or anything not present in the evidence.

Return only valid JSON with this exact shape:
{{"explanation": "one concise explanation, 1-2 sentences"}}

Track:
- name: {track.track_name}
- artist: {track.artist_name}
- genre: {track.genre}
- retrieval_score: {result.score:.2f}
- derived_vibe_tags: {vibe_tags}

Retrieval evidence:
{evidence_lines}
""".strip()


def _generate_gemini_response_text(result: RetrievalResult, model: str) -> Optional[str]:
    """
    Call Gemini and return the raw response text.
    """
    from google import genai
    from google.genai import types

    client = genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=build_gemini_prompt(result),
        config=types.GenerateContentConfig(
            temperature=0.2,
            candidate_count=1,
            max_output_tokens=180,
        ),
    )
    return getattr(response, "text", None)


def parse_gemini_explanation(raw_response: str) -> Optional[str]:
    """
    Parse Gemini output into one explanation string.

    Accepts plain JSON and JSON wrapped in Markdown code fences. Returns None
    when the response is malformed or missing explanation text.
    """
    cleaned = _strip_json_code_fence(raw_response.strip())

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    explanation = payload.get("explanation")
    if not isinstance(explanation, str):
        return None

    explanation = explanation.strip()
    if not explanation:
        return None

    return explanation


def _strip_json_code_fence(text: str) -> str:
    """
    Remove Markdown JSON code fences if the model includes them.
    """
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text


def _has_gemini_api_key() -> bool:
    """
    Check for either supported Gemini API key environment variable.
    """
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def _deterministic_fallback(
    result: RetrievalResult,
    reason: str,
) -> LLMExplanationResult:
    """
    Return the deterministic explanation when Gemini cannot be used safely.
    """
    return LLMExplanationResult(
        explanation=explain_recommendation(result),
        used_llm=False,
        raw_response=None,
        fallback_reason=reason,
        guardrail_report=None,
    )
