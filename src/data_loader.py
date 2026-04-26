import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .recommender import Song


@dataclass(frozen=True)
class TrackRecord:
    """
    Normalized track data from the real Spotify-style CSV dataset.
    """

    track_name: str
    artist_name: str
    album_name: str
    genre: str
    vibe_tags: List[str]
    popularity: float
    danceability: float
    energy: float
    acousticness: float
    valence: float
    tempo: float


REQUIRED_COLUMNS = {
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
}


def load_track_records(csv_path: str, limit: Optional[int] = None) -> List[TrackRecord]:
    """
    Load Spotify-style CSV rows into normalized TrackRecord objects.

    Invalid rows are skipped so one bad record does not break the whole benchmark.
    """
    path = Path(csv_path)
    records: List[TrackRecord] = []

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        _validate_columns(reader.fieldnames)

        for row in reader:
            if limit is not None and len(records) >= limit:
                break

            try:
                records.append(_row_to_track_record(row))
            except (KeyError, ValueError):
                continue

    return records


def records_to_songs(records: List[TrackRecord]) -> List[Song]:
    """
    Convert TrackRecord objects into Song objects used by the original recommender.

    For real Spotify-style records, mood is represented as a pipe-separated summary
    of derived vibe tags because the source dataset does not contain ground-truth mood.
    """
    songs: List[Song] = []

    for index, record in enumerate(records, start=1):
        songs.append(
            Song(
                id=index,
                title=record.track_name,
                artist=record.artist_name,
                genre=record.genre,
                mood="|".join(record.vibe_tags),
                energy=record.energy,
                tempo_bpm=record.tempo,
                valence=record.valence,
                danceability=record.danceability,
                acousticness=record.acousticness,
            )
        )

    return songs


def infer_vibe_tags(
    energy: float,
    valence: float,
    acousticness: float,
    danceability: float,
    tempo: float,
) -> List[str]:
    """
    Infer evidence-based vibe tags from audio features.

    These are derived descriptors, not ground-truth mood labels.
    """
    tags: List[str] = []

    if energy >= 0.75:
        tags.append("high_energy")

    if energy <= 0.45:
        tags.append("low_energy")

    if valence >= 0.65:
        tags.append("positive")

    if valence < 0.45:
        tags.append("darker")

    if acousticness >= 0.65:
        tags.append("acoustic")

    if acousticness <= 0.25:
        tags.append("electronic")

    if danceability >= 0.70:
        tags.append("danceable")

    if tempo >= 130:
        tags.append("fast_tempo")

    if tempo <= 85:
        tags.append("slow_tempo")

    if not tags:
        tags.append("moderate_profile")

    return tags


def _validate_columns(fieldnames: Optional[List[str]]) -> None:
    """
    Make sure the CSV has the columns this project expects.
    """
    if fieldnames is None:
        raise ValueError("CSV file is missing a header row.")

    missing_columns = REQUIRED_COLUMNS.difference(fieldnames)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV file is missing required columns: {missing}")


def _row_to_track_record(row: dict) -> TrackRecord:
    """
    Convert one raw CSV row into a TrackRecord.
    """
    track_name = row["track_name"].strip()
    artist_name = row["artists"].strip()
    album_name = row["album_name"].strip()
    genre = row["track_genre"].strip()

    if not track_name or not artist_name or not genre:
        raise ValueError("Track row is missing required text fields.")

    popularity = _parse_float(row["popularity"])
    danceability = _parse_float(row["danceability"])
    energy = _parse_float(row["energy"])
    acousticness = _parse_float(row["acousticness"])
    valence = _parse_float(row["valence"])
    tempo = _parse_float(row["tempo"])

    vibe_tags = infer_vibe_tags(
        energy=energy,
        valence=valence,
        acousticness=acousticness,
        danceability=danceability,
        tempo=tempo,
    )

    return TrackRecord(
        track_name=track_name,
        artist_name=artist_name,
        album_name=album_name,
        genre=genre,
        vibe_tags=vibe_tags,
        popularity=popularity,
        danceability=danceability,
        energy=energy,
        acousticness=acousticness,
        valence=valence,
        tempo=tempo,
    )


def _parse_float(value: str) -> float:
    """
    Parse a numeric CSV value.
    """
    return float(value.strip())
