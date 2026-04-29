import pandas as pd
import pytest

from scripts.create_spotify_sample import LOADER_COLUMNS, create_sample


@pytest.fixture
def source_csv(tmp_path):
    source_path = tmp_path / "full_dataset.csv"
    rows = []
    for index in range(10):
        rows.append(
            {
                "track_name": f"Track {index}",
                "artists": f"Artist {index}",
                "album_name": f"Album {index}",
                "track_genre": "pop" if index % 2 == 0 else "rock",
                "popularity": 50 + index,
                "danceability": 0.50 + index * 0.01,
                "energy": 0.60 + index * 0.01,
                "acousticness": 0.20 + index * 0.01,
                "valence": 0.55 + index * 0.01,
                "tempo": 100 + index,
                "unused_column": f"unused {index}",
            }
        )

    pd.DataFrame(rows).to_csv(source_path, index=False)
    return source_path


def test_create_sample_writes_deterministic_loader_columns(source_csv, tmp_path):
    first_output = tmp_path / "sample_first.csv"
    second_output = tmp_path / "sample_second.csv"

    create_sample(
        source_url=str(source_csv),
        output_path=str(first_output),
        sample_size=5,
        random_seed=7,
    )
    create_sample(
        source_url=str(source_csv),
        output_path=str(second_output),
        sample_size=5,
        random_seed=7,
    )

    first = pd.read_csv(first_output)
    second = pd.read_csv(second_output)

    assert list(first.columns) == LOADER_COLUMNS
    assert len(first) == 5
    assert first.equals(second)


def test_create_sample_reports_missing_columns(tmp_path):
    source_path = tmp_path / "bad_dataset.csv"
    pd.DataFrame(
        [
            {
                "track_name": "Track",
                "artists": "Artist",
            }
        ]
    ).to_csv(source_path, index=False)

    with pytest.raises(ValueError, match="Source dataset is missing required columns"):
        create_sample(
            source_url=str(source_path),
            output_path=str(tmp_path / "sample.csv"),
            sample_size=1,
        )
