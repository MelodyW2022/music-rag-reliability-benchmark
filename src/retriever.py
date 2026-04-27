from dataclasses import dataclass
from typing import List, Tuple

from .data_loader import TrackRecord


@dataclass(frozen=True)
class RetrievalQuery:
    """
    User preference query for retrieval over real track records.
    """

    preferred_genre: str
    target_energy: float
    target_acousticness: float
    target_valence: float
    target_danceability: float


@dataclass(frozen=True)
class RetrievalResult:
    """
    One retrieved track with its score and evidence.
    """

    track: TrackRecord
    score: float
    evidence: List[str]


def retrieve_tracks(
    query: RetrievalQuery,
    records: List[TrackRecord],
    k: int = 5,
) -> List[RetrievalResult]:
    """
    Retrieve the top k tracks using genre and audio-feature similarity.
    """
    scored_results: List[RetrievalResult] = []

    for record in records:
        score, evidence = score_track(query, record)
        scored_results.append(
            RetrievalResult(
                track=record,
                score=score,
                evidence=evidence,
            )
        )

    scored_results.sort(key=lambda result: result.score, reverse=True)
    return scored_results[:k]


def score_track(query: RetrievalQuery, record: TrackRecord) -> Tuple[float, List[str]]:
    """
    Score one track against the query and collect retrieval evidence.

    Vibe tags are explanation evidence only, not extra scoring signals, to avoid
    double-counting derived labels and their source features.
    """
    score = 0.0
    evidence: List[str] = []

    if record.genre == query.preferred_genre:
        score += 2.0
        evidence.append(f"genre matches preferred genre '{query.preferred_genre}' (+2.00)")
    else:
        evidence.append(
            f"genre differs from preferred genre: '{record.genre}' vs '{query.preferred_genre}' (+0.00)"
        )

    energy_points = 2.0 * similarity(record.energy, query.target_energy)
    score += energy_points
    evidence.append(
        f"energy closeness: {record.energy:.2f} vs target {query.target_energy:.2f} (+{energy_points:.2f})"
    )

    acoustic_points = 1.0 * similarity(
        record.acousticness,
        query.target_acousticness,
    )
    score += acoustic_points
    evidence.append(
        f"acousticness closeness: {record.acousticness:.2f} vs target {query.target_acousticness:.2f} (+{acoustic_points:.2f})"
    )

    valence_points = 1.0 * similarity(record.valence, query.target_valence)
    score += valence_points
    evidence.append(
        f"valence closeness: {record.valence:.2f} vs target {query.target_valence:.2f} (+{valence_points:.2f})"
    )

    danceability_points = 0.75 * similarity(
        record.danceability,
        query.target_danceability,
    )
    score += danceability_points
    evidence.append(
        f"danceability closeness: {record.danceability:.2f} vs target {query.target_danceability:.2f} (+{danceability_points:.2f})"
    )

    evidence.append(f"derived vibe tags for explanation: {', '.join(record.vibe_tags)}")

    return score, evidence


def similarity(actual: float, target: float) -> float:
    """
    Return a bounded similarity score where 1.0 means exact match.
    """
    return max(0.0, 1 - abs(actual - target))
