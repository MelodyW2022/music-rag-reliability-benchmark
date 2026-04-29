"""
Create a deterministic sample from the Hugging Face Spotify Tracks Dataset.

Run:
    python3 scripts/create_spotify_sample.py

Output:
    data/spotify_tracks_sample_500.csv
"""

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_SOURCE_URL = (
    "https://huggingface.co/datasets/maharshipandya/"
    "spotify-tracks-dataset/resolve/main/dataset.csv"
)
DEFAULT_OUTPUT_PATH = "data/spotify_tracks_sample_500.csv"
DEFAULT_SAMPLE_SIZE = 500
DEFAULT_RANDOM_SEED = 42

LOADER_COLUMNS = [
    "track_name",
    "artists",
    "album_name",
    "track_genre",
    "popularity",
    "danceability",
    "energy",
    "acousticness",
    "valence",
    "tempo",
]


def create_sample(
    source_url: str = DEFAULT_SOURCE_URL,
    output_path: str = DEFAULT_OUTPUT_PATH,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> Path:
    """
    Download the full Spotify-style dataset and write a deterministic sample.

    The output keeps only the columns required by src.data_loader.load_track_records.
    Rows with missing required values are dropped before sampling.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(source_url)
    _validate_columns(frame)

    cleaned = frame[LOADER_COLUMNS].dropna()
    if len(cleaned) < sample_size:
        raise ValueError(
            f"Cannot sample {sample_size} rows from only {len(cleaned)} valid rows."
        )

    sample = cleaned.sample(
        n=sample_size,
        random_state=random_seed,
    ).sort_index()

    sample.to_csv(output, index=False)
    return output


def _validate_columns(frame: pd.DataFrame) -> None:
    """
    Ensure the source dataset has the columns required by the project loader.
    """
    missing_columns = set(LOADER_COLUMNS).difference(frame.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Source dataset is missing required columns: {missing}")


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command line parser for deterministic dataset sampling.
    """
    parser = argparse.ArgumentParser(
        description="Create a deterministic Spotify Tracks Dataset sample."
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="CSV URL or local path for the full Spotify Tracks Dataset.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help="Where to write the sampled CSV.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="Number of rows to sample.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed for deterministic sampling.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output = create_sample(
        source_url=args.source_url,
        output_path=args.output,
        sample_size=args.sample_size,
        random_seed=args.random_seed,
    )
    print(f"Wrote deterministic sample to {output}")


if __name__ == "__main__":
    main()
