import pytest

from src.data_loader import TrackRecord
from src.retriever import RetrievalQuery, retrieve_tracks, similarity


def make_track(
    track_name: str,
    genre: str,
    energy: float,
    acousticness: float,
    valence: float,
    danceability: float,
    vibe_tags: list[str],
) -> TrackRecord:
    return TrackRecord(
        track_name=track_name,
        artist_name="Test Artist",
        album_name="Test Album",
        genre=genre,
        vibe_tags=vibe_tags,
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
        target_valence=0.75,
        target_danceability=0.80,
    )


def test_retrieve_tracks_returns_top_k_results():
    records = [
        make_track("Strong Match", "pop", 0.82, 0.18, 0.76, 0.81, ["high_energy"]),
        make_track("Second Match", "pop", 0.70, 0.30, 0.70, 0.75, ["positive"]),
        make_track("Weak Match", "jazz", 0.20, 0.95, 0.30, 0.35, ["low_energy"]),
    ]

    results = retrieve_tracks(make_query(), records, k=2)

    assert len(results) == 2
    assert [result.track.track_name for result in results] == [
        "Strong Match",
        "Second Match",
    ]


def test_retrieve_tracks_ranks_stronger_matches_first():
    records = [
        make_track("Weak Match", "jazz", 0.20, 0.95, 0.30, 0.35, ["low_energy"]),
        make_track(
            "Strong Match",
            "pop",
            0.82,
            0.18,
            0.76,
            0.81,
            ["high_energy", "positive", "danceable"],
        ),
    ]

    results = retrieve_tracks(make_query(), records, k=2)

    assert results[0].track.track_name == "Strong Match"
    assert results[0].score > results[1].score


def test_retrieve_tracks_includes_grounding_evidence():
    records = [
        make_track(
            "Strong Match",
            "pop",
            0.82,
            0.18,
            0.76,
            0.81,
            ["high_energy", "positive", "danceable"],
        )
    ]

    results = retrieve_tracks(make_query(), records, k=1)
    evidence = " ".join(results[0].evidence)

    assert "genre matches" in evidence
    assert "energy closeness" in evidence
    assert "acousticness closeness" in evidence
    assert "valence closeness" in evidence
    assert "danceability closeness" in evidence
    assert "derived vibe tags" in evidence


def test_similarity_is_bounded():
    assert similarity(0.8, 0.8) == 1.0
    assert similarity(0.8, 0.6) == pytest.approx(0.8)
    assert similarity(3.0, 0.0) == 0.0
