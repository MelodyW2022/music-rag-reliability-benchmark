import pytest

from src.data_loader import infer_vibe_tags, load_track_records, records_to_songs


def test_infer_vibe_tags_returns_audio_feature_evidence():
    tags = infer_vibe_tags(
        energy=0.82,
        valence=0.72,
        acousticness=0.18,
        danceability=0.77,
        tempo=136,
    )

    assert tags == [
        "high_energy",
        "positive",
        "electronic",
        "danceable",
        "fast_tempo",
    ]


def test_infer_vibe_tags_returns_neutral_fallback():
    tags = infer_vibe_tags(
        energy=0.60,
        valence=0.55,
        acousticness=0.45,
        danceability=0.50,
        tempo=100,
    )

    assert tags == ["moderate_profile"]


def test_load_track_records_normalizes_spotify_style_csv(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    csv_path.write_text(
        "track_name,artists,album_name,track_genre,popularity,"
        "danceability,energy,acousticness,valence,tempo\n"
        "Sample Track,Sample Artist,Sample Album,pop,71,"
        "0.77,0.82,0.18,0.72,136\n",
        encoding="utf-8",
    )

    records = load_track_records(str(csv_path))

    assert len(records) == 1
    assert records[0].track_name == "Sample Track"
    assert records[0].artist_name == "Sample Artist"
    assert records[0].genre == "pop"
    assert records[0].vibe_tags == [
        "high_energy",
        "positive",
        "electronic",
        "danceable",
        "fast_tempo",
    ]


def test_records_to_songs_preserves_track_features(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    csv_path.write_text(
        "track_name,artists,album_name,track_genre,popularity,"
        "danceability,energy,acousticness,valence,tempo\n"
        "Sample Track,Sample Artist,Sample Album,pop,71,"
        "0.77,0.82,0.18,0.72,136\n",
        encoding="utf-8",
    )

    records = load_track_records(str(csv_path))
    songs = records_to_songs(records)

    assert len(songs) == 1
    assert songs[0].title == "Sample Track"
    assert songs[0].artist == "Sample Artist"
    assert songs[0].mood == "high_energy|positive|electronic|danceable|fast_tempo"
    assert songs[0].energy == 0.82
    assert songs[0].tempo_bpm == 136


def test_load_track_records_reports_missing_columns(tmp_path):
    csv_path = tmp_path / "bad_tracks.csv"
    csv_path.write_text(
        "track_name,artists\n"
        "Sample Track,Sample Artist\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        load_track_records(str(csv_path))
