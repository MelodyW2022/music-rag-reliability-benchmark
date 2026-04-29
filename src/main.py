"""
Tiny command line demo for the retrieval-grounded music recommender.

Run:
    python3 -m src.main demo
    python3 -m src.main demo --csv data/spotify_tracks_sample_500.csv
"""

import argparse
from pathlib import Path
from typing import List, Optional

from .data_loader import TrackRecord, load_track_records
from .explainer import explain_recommendations
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


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command line parser for the demo.
    """
    parser = argparse.ArgumentParser(
        description="Run a retrieval-grounded music recommendation demo."
    )
    parser.add_argument(
        "command",
        choices=["demo"],
        help="Command to run. Currently only 'demo' is supported.",
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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "demo":
        run_demo(csv_path=args.csv, limit=args.limit)


if __name__ == "__main__":
    main()
