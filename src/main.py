"""
Tiny command line demo for the retrieval-grounded music recommender.

Run:
    python3 -m src.main demo
"""

import argparse
from typing import List

from .data_loader import TrackRecord
from .explainer import explain_recommendations
from .retriever import RetrievalQuery, retrieve_tracks


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


def run_demo() -> None:
    """
    Run the loader-free demo pipeline: records -> retrieve -> explain -> print.
    """
    records = make_demo_records()
    query = make_demo_query()

    retrieved = retrieve_tracks(query=query, records=records, k=3)
    explanations = explain_recommendations(retrieved)

    print("RAG-grounded music recommendation demo")
    print("=" * 48)

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
    Build the minimal command line parser for tonight's demo.
    """
    parser = argparse.ArgumentParser(
        description="Run a tiny retrieval-grounded music recommendation demo."
    )
    parser.add_argument(
        "command",
        choices=["demo"],
        help="Command to run. Currently only 'demo' is supported.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "demo":
        run_demo()


if __name__ == "__main__":
    main()
