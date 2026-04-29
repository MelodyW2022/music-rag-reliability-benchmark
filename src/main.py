"""
Tiny command line demo for the retrieval-grounded music recommender.

Run:
    python3 -m src.main demo
    python3 -m src.main trace
    python3 -m src.main evaluate
    python3 -m src.main demo --csv data/spotify_tracks_sample_500.csv
"""

import argparse
from pathlib import Path
from typing import List, Optional

from .data_loader import TrackRecord, load_track_records
from .evaluator import evaluate_records, explain_from_raw_response
from .explainer import explain_recommendations
from .llm_explainer import explain_with_gemini
from .retriever import RetrievalQuery, retrieve_tracks


DEFAULT_REAL_DATASET_PATH = "data/spotify_tracks_sample_500.csv"


def make_demo_records() -> List[TrackRecord]:
    """
    Create a tiny real-data-shaped catalog so the RAG flow can run end-to-end.
    """
    return [
        TrackRecord(
            track_name="Sample Pop Signal",
            artist_name="Demo Artist",
            album_name="Demo Album",
            genre="pop",
            vibe_tags=["high_energy", "positive", "danceable"],
            popularity=71.0,
            danceability=0.82,
            energy=0.84,
            acousticness=0.18,
            valence=0.86,
            tempo=124.0,
        ),
        TrackRecord(
            track_name="Quiet Study Loop",
            artist_name="Demo Artist",
            album_name="Demo Album",
            genre="lofi",
            vibe_tags=["low_energy", "acoustic", "slow_tempo"],
            popularity=54.0,
            danceability=0.56,
            energy=0.36,
            acousticness=0.82,
            valence=0.58,
            tempo=78.0,
        ),
        TrackRecord(
            track_name="Heavy Motion",
            artist_name="Demo Artist",
            album_name="Demo Album",
            genre="rock",
            vibe_tags=["high_energy", "electronic", "fast_tempo"],
            popularity=63.0,
            danceability=0.66,
            energy=0.91,
            acousticness=0.09,
            valence=0.46,
            tempo=148.0,
        ),
    ]


def load_demo_records(csv_path: Optional[str], limit: Optional[int]) -> List[TrackRecord]:
    """
    Load real CSV records when available, otherwise use the tiny built-in catalog.
    """
    if csv_path and Path(csv_path).exists():
        return load_track_records(csv_path, limit=limit)

    return make_demo_records()


def make_demo_query() -> RetrievalQuery:
    """
    Create one hardcoded query for a high-energy pop recommendation demo.
    """
    return RetrievalQuery(
        preferred_genre="pop",
        target_energy=0.80,
        target_acousticness=0.20,
        target_valence=0.85,
        target_danceability=0.80,
    )


def run_demo(
    csv_path: Optional[str] = DEFAULT_REAL_DATASET_PATH,
    limit: Optional[int] = None,
) -> None:
    """
    Run the demo pipeline: records -> retrieve -> explain -> print.
    """
    records = load_demo_records(csv_path=csv_path, limit=limit)
    query = make_demo_query()

    retrieved = retrieve_tracks(query=query, records=records, k=5)
    explanations = explain_recommendations(retrieved)

    print("RAG-grounded music recommendation demo")
    print("=" * 48)
    print(f"Catalog size: {len(records)}")
    print()

    for index, item in enumerate(explanations, start=1):
        print(f"{index}. {item.track_name} by {item.artist_name}")
        print(f"   Genre: {item.genre}")
        print(f"   Score: {item.score:.2f}")
        print(f"   Explanation: {item.explanation}")
        print("   Evidence:")
        for evidence_item in item.evidence:
            print(f"   - {evidence_item}")
        print()


def run_trace(
    csv_path: Optional[str] = DEFAULT_REAL_DATASET_PATH,
    limit: Optional[int] = None,
    use_gemini: bool = False,
) -> None:
    """
    Show one retrieval-to-explanation trace with guardrail behavior.
    """
    records = load_demo_records(csv_path=csv_path, limit=limit)
    query = make_demo_query()
    result = retrieve_tracks(query=query, records=records, k=1)[0]

    print("RAG trace with guardrail validation")
    print("=" * 48)
    print(f"Catalog size: {len(records)}")
    print(
        "Query: genre=pop, energy=0.80, acousticness=0.20, "
        "valence=0.85, danceability=0.80"
    )
    print(f"Top retrieved track: {result.track.track_name} by {result.track.artist_name}")
    print(f"Retrieval score: {result.score:.2f}")
    print("Retrieval evidence:")
    for evidence_item in result.evidence:
        print(f"- {evidence_item}")
    print()

    if use_gemini:
        llm_result = explain_with_gemini(result)
        print("Gemini mode: live call if API key/package are available")
    else:
        raw_response = (
            '{"explanation": "This track has emotional lyrics and rich vocals."}'
        )
        llm_result = explain_from_raw_response(result, raw_response)
        print("Gemini mode: simulated unsafe raw response for reliability demo")

    print(f"Raw response: {llm_result.raw_response}")
    print(f"Used LLM output: {llm_result.used_llm}")
    print(f"Fallback reason: {llm_result.fallback_reason or 'none'}")
    if llm_result.guardrail_report:
        print(
            "Guardrail unsupported terms: "
            f"{llm_result.guardrail_report.unsupported_terms}"
        )
    print(f"Final safe explanation: {llm_result.explanation.explanation}")


def run_evaluate(
    csv_path: Optional[str] = DEFAULT_REAL_DATASET_PATH,
    limit: Optional[int] = None,
    use_gemini: bool = False,
    simulate_llm_failures: bool = True,
) -> None:
    """
    Run the predefined reliability evaluator and print summary metrics.
    """
    records = load_demo_records(csv_path=csv_path, limit=limit)
    summary = evaluate_records(
        records=records,
        use_gemini=use_gemini,
        simulate_llm_failures=simulate_llm_failures,
    )

    print("Reliability evaluation")
    print("=" * 48)
    print(f"Catalog size: {len(records)}")
    print(f"Evaluation cases: {len(summary.items)}")
    print(f"Unsupported claim rate: {summary.unsupported_claim_rate:.2f}")
    print(f"Fallback rate: {summary.fallback_rate:.2f}")
    print(f"Format failure rate: {summary.format_failure_rate:.2f}")
    print(f"Global evidence coverage: {summary.global_evidence_coverage:.2f}")
    print()

    for item in summary.items:
        print(f"- {item.case_name}: {item.track_name}")
        print(f"  used_llm={item.used_llm}")
        print(f"  fallback_reason={item.fallback_reason or 'none'}")
        if item.raw_guardrail_report:
            print(f"  unsupported_terms={item.raw_guardrail_report.unsupported_terms}")
        print(f"  final_passed={item.final_guardrail_report.passed}")


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command line parser for the demo.
    """
    parser = argparse.ArgumentParser(
        description="Run a retrieval-grounded music recommendation demo."
    )
    parser.add_argument(
        "command",
        choices=["demo", "trace", "evaluate"],
        help="Command to run.",
    )
    parser.add_argument(
        "--csv",
        default=DEFAULT_REAL_DATASET_PATH,
        help="Spotify-style CSV path to load for the demo.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of CSV records to load.",
    )
    parser.add_argument(
        "--use-gemini",
        action="store_true",
        help="Use live Gemini explanation generation when credentials are available.",
    )
    parser.add_argument(
        "--no-simulated-failures",
        action="store_true",
        help="Disable simulated LLM failures for evaluate.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "demo":
        run_demo(csv_path=args.csv, limit=args.limit)
    elif args.command == "trace":
        run_trace(csv_path=args.csv, limit=args.limit, use_gemini=args.use_gemini)
    elif args.command == "evaluate":
        run_evaluate(
            csv_path=args.csv,
            limit=args.limit,
            use_gemini=args.use_gemini,
            simulate_llm_failures=not args.no_simulated_failures,
        )


if __name__ == "__main__":
    main()
