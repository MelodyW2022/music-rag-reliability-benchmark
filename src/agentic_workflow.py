from dataclasses import dataclass
from typing import List, Optional

from .data_loader import TrackRecord
from .guardrails import REQUIRED_EVIDENCE_MARKERS
from .retriever import RetrievalQuery, RetrievalResult, retrieve_tracks


DEFAULT_WORKFLOW_K = 3


@dataclass(frozen=True)
class WorkflowTraceStep:
    """
    One auditable step in the deterministic agent workflow.
    """

    phase: str
    step_name: str
    tool_used: str
    decision: str
    result: str


@dataclass(frozen=True)
class EvidenceEvaluation:
    """
    Evidence completeness check for one retrieved candidate.
    """

    passed: bool
    matched_markers: List[str]
    missing_markers: List[str]


@dataclass(frozen=True)
class AgenticWorkflowResult:
    """
    Result of the agentic retrieval workflow.

    Later workflow checkpoints will add explanation and guardrail decisions on
    top of this selected retrieval result and trace.
    """

    query: RetrievalQuery
    selected_result: Optional[RetrievalResult]
    evidence_evaluation: Optional[EvidenceEvaluation]
    trace: List[WorkflowTraceStep]
    fallback_reason: Optional[str]


def run_agentic_workflow(
    records: List[TrackRecord],
    query: Optional[RetrievalQuery] = None,
    k: int = DEFAULT_WORKFLOW_K,
) -> AgenticWorkflowResult:
    """
    Run the first half of the agent loop: plan, retrieve, evaluate, reflect.

    The loop is deterministic so the benchmark remains reproducible. It only
    retries another retrieved candidate when the current candidate is missing
    required grounding evidence.
    """
    planned_query = query or build_default_query()
    trace: List[WorkflowTraceStep] = [
        WorkflowTraceStep(
            phase="Planner",
            step_name="Plan user query",
            tool_used="RetrievalQuery",
            decision="Build grounded recommendation plan",
            result=_summarize_query(planned_query),
        )
    ]

    retrieved_results = retrieve_tracks(query=planned_query, records=records, k=k)
    trace.append(
        WorkflowTraceStep(
            phase="Executor",
            step_name="Retrieve candidate tracks",
            tool_used="retrieve_tracks",
            decision=f"Retrieve top {k} candidate tracks",
            result=f"Retrieved {len(retrieved_results)} candidate(s)",
        )
    )

    if not retrieved_results:
        trace.append(
            WorkflowTraceStep(
                phase="Reflector",
                step_name="Reflect on retrieval evidence",
                tool_used="retry policy",
                decision="Stop workflow because retrieval returned no candidates",
                result="No recommendation available",
            )
        )
        return AgenticWorkflowResult(
            query=planned_query,
            selected_result=None,
            evidence_evaluation=None,
            trace=trace,
            fallback_reason="retrieval returned no candidates",
        )

    for attempt_index, candidate in enumerate(retrieved_results, start=1):
        evidence_evaluation = evaluate_evidence(candidate)
        trace.append(
            WorkflowTraceStep(
                phase="Evaluator",
                step_name="Evaluate evidence strength",
                tool_used="evidence marker check",
                decision=(
                    "Evidence complete"
                    if evidence_evaluation.passed
                    else "Evidence incomplete"
                ),
                result=_summarize_evidence_evaluation(evidence_evaluation),
            )
        )

        if evidence_evaluation.passed:
            trace.append(
                WorkflowTraceStep(
                    phase="Reflector",
                    step_name="Reflect on retrieval evidence",
                    tool_used="retry policy",
                    decision="Continue with selected candidate",
                    result=(
                        f"Selected {candidate.track.track_name} "
                        f"on attempt {attempt_index}"
                    ),
                )
            )
            return AgenticWorkflowResult(
                query=planned_query,
                selected_result=candidate,
                evidence_evaluation=evidence_evaluation,
                trace=trace,
                fallback_reason=None,
            )

        trace.append(
            WorkflowTraceStep(
                phase="Reflector",
                step_name="Reflect on retrieval evidence",
                tool_used="retry policy",
                decision="Retry next candidate",
                result=(
                    f"Rejected {candidate.track.track_name}; "
                    f"missing evidence: {', '.join(evidence_evaluation.missing_markers)}"
                ),
            )
        )

    return AgenticWorkflowResult(
        query=planned_query,
        selected_result=None,
        evidence_evaluation=None,
        trace=trace,
        fallback_reason="no retrieved candidate had complete grounding evidence",
    )


def build_default_query() -> RetrievalQuery:
    """
    Build the default high-energy pop query used by demos.
    """
    return RetrievalQuery(
        preferred_genre="pop",
        target_energy=0.80,
        target_acousticness=0.20,
        target_valence=0.85,
        target_danceability=0.80,
    )


def evaluate_evidence(result: RetrievalResult) -> EvidenceEvaluation:
    """
    Check whether a retrieved candidate includes required grounding evidence.
    """
    normalized_evidence = " ".join(result.evidence).lower()
    matched_markers = [
        marker
        for marker in REQUIRED_EVIDENCE_MARKERS
        if marker in normalized_evidence
    ]
    missing_markers = [
        marker
        for marker in REQUIRED_EVIDENCE_MARKERS
        if marker not in normalized_evidence
    ]

    return EvidenceEvaluation(
        passed=len(missing_markers) == 0,
        matched_markers=matched_markers,
        missing_markers=missing_markers,
    )


def _summarize_query(query: RetrievalQuery) -> str:
    """
    Format the planned query for trace output.
    """
    return (
        f"genre={query.preferred_genre}, energy={query.target_energy:.2f}, "
        f"acousticness={query.target_acousticness:.2f}, "
        f"valence={query.target_valence:.2f}, "
        f"danceability={query.target_danceability:.2f}"
    )


def _summarize_evidence_evaluation(evaluation: EvidenceEvaluation) -> str:
    """
    Format evidence marker coverage for trace output.
    """
    if evaluation.passed:
        return f"Matched all {len(evaluation.matched_markers)} evidence markers"

    return (
        f"Matched {len(evaluation.matched_markers)} marker(s); "
        f"missing: {', '.join(evaluation.missing_markers)}"
    )
