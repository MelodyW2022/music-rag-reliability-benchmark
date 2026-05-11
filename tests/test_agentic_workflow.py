from src import agentic_workflow
from src.agentic_workflow import evaluate_evidence, run_agentic_workflow
from src.data_loader import TrackRecord
from src.retriever import RetrievalQuery, RetrievalResult


def make_track(
    track_name: str,
    genre: str = "pop",
    energy: float = 0.82,
    acousticness: float = 0.18,
    valence: float = 0.86,
    danceability: float = 0.81,
) -> TrackRecord:
    return TrackRecord(
        track_name=track_name,
        artist_name="Test Artist",
        album_name="Test Album",
        genre=genre,
        vibe_tags=["high_energy", "positive", "danceable"],
        popularity=50.0,
        danceability=danceability,
        energy=energy,
        acousticness=acousticness,
        valence=valence,
        tempo=120.0,
    )


def make_query() -> RetrievalQuery:
    return RetrievalQuery(
        preferred_genre="pop",
        target_energy=0.80,
        target_acousticness=0.20,
        target_valence=0.85,
        target_danceability=0.80,
    )


def make_complete_result() -> RetrievalResult:
    return RetrievalResult(
        track=make_track("Strong Match"),
        score=6.50,
        evidence=[
            "genre matches preferred genre 'pop' (+2.00)",
            "energy closeness: 0.82 vs target 0.80 (+1.96)",
            "acousticness closeness: 0.18 vs target 0.20 (+0.98)",
            "valence closeness: 0.86 vs target 0.85 (+0.99)",
            "danceability closeness: 0.81 vs target 0.80 (+0.74)",
            "derived vibe tags for explanation: high_energy, positive, danceable",
        ],
    )


def test_evaluate_evidence_passes_when_all_markers_are_present():
    evaluation = evaluate_evidence(make_complete_result())

    assert evaluation.passed
    assert evaluation.missing_markers == []
    assert "genre" in evaluation.matched_markers
    assert "danceability closeness" in evaluation.matched_markers


def test_evaluate_evidence_fails_when_markers_are_missing():
    result = RetrievalResult(
        track=make_track("Incomplete Evidence"),
        score=4.00,
        evidence=[
            "genre matches preferred genre 'pop' (+2.00)",
            "energy closeness: 0.82 vs target 0.80 (+1.96)",
        ],
    )

    evaluation = evaluate_evidence(result)

    assert not evaluation.passed
    assert "acousticness closeness" in evaluation.missing_markers
    assert "valence closeness" in evaluation.missing_markers
    assert "danceability closeness" in evaluation.missing_markers


def test_workflow_trace_contains_agent_loop_phases():
    result = run_agentic_workflow(records=[make_track("Strong Match")], query=make_query())

    phases = [step.phase for step in result.trace]

    assert "Planner" in phases
    assert "Executor" in phases
    assert "Evaluator" in phases
    assert "Reflector" in phases
    assert result.selected_result is not None
    assert result.selected_result.track.track_name == "Strong Match"


def test_workflow_does_not_retry_when_evidence_is_complete():
    result = run_agentic_workflow(records=[make_track("Strong Match")], query=make_query())

    decisions = [step.decision for step in result.trace]

    assert "Continue with selected candidate" in decisions
    assert "Retry next candidate" not in decisions
    assert result.fallback_reason is None


def test_workflow_retries_next_candidate_when_evidence_is_incomplete(monkeypatch):
    incomplete_result = RetrievalResult(
        track=make_track("Incomplete Evidence"),
        score=7.00,
        evidence=[
            "genre matches preferred genre 'pop' (+2.00)",
            "energy closeness: 0.82 vs target 0.80 (+1.96)",
        ],
    )
    complete_result = make_complete_result()

    def fake_retrieve_tracks(query, records, k):
        return [incomplete_result, complete_result]

    monkeypatch.setattr(agentic_workflow, "retrieve_tracks", fake_retrieve_tracks)

    result = run_agentic_workflow(records=[make_track("Unused")], query=make_query())
    decisions = [step.decision for step in result.trace]

    assert "Retry next candidate" in decisions
    assert "Continue with selected candidate" in decisions
    assert result.selected_result == complete_result
    assert result.fallback_reason is None


def test_workflow_records_no_candidate_fallback_when_retrieval_is_empty():
    result = run_agentic_workflow(records=[], query=make_query())

    assert result.selected_result is None
    assert result.fallback_reason == "retrieval returned no candidates"
    assert result.trace[-1].phase == "Reflector"
    assert "no candidates" in result.trace[-1].decision
