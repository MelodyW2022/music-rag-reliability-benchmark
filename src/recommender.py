import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_acousticness: float
    target_valence: float


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Score one song against one user profile and collect the reasons.
        """
        score = 0.0
        reasons: List[str] = []

        if song.mood == user.favorite_mood:
            score += 3.0
            reasons.append("mood match (+3.0)")

        if song.genre == user.favorite_genre:
            score += 2.0
            reasons.append("genre match (+2.0)")

        energy_similarity = 1 - abs(song.energy - user.target_energy)
        energy_points = 2.0 * energy_similarity
        score += energy_points
        reasons.append(f"energy similarity (+{energy_points:.2f})")

        acoustic_similarity = 1 - abs(song.acousticness - user.target_acousticness)
        acoustic_points = 1.0 * acoustic_similarity
        score += acoustic_points
        reasons.append(f"acoustic similarity (+{acoustic_points:.2f})")

        valence_similarity = 1 - abs(song.valence - user.target_valence)
        valence_points = 0.5 * valence_similarity
        score += valence_points
        reasons.append(f"valence similarity (+{valence_points:.2f})")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Rank all songs by score and return the top k songs.
        """
        scored_songs: List[Tuple[Song, float]] = []

        for song in self.songs:
            score, _ = self._score_song(user, song)
            scored_songs.append((song, score))

        scored_songs.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Return a short explanation string for why this song was recommended.
        """
        _, reasons = self._score_song(user, song)
        return f"{song.title} fits your profile because {', '.join(reasons)}."


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dictionaries."""
    # Implement CSV loading logic
    print(f"Loading songs from {csv_path}...")
    songs = []

    # open the file safely
    # "with" automatically closes it afterwards
    # newline="" is the recommended way when using csv, it means don't pre-process newline characters in a special way and let the csv module interpret rows properly
    # encoding="utf-8" is a safe default

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        # reader is an interator over rows and each row is a dict with keys from the header
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            }
            songs.append(song)

    return songs


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score, rank, and return the top k song recommendations."""
    #  Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        # Return up to k songs, but only include songs whose score is greater than 0.
        if score > 0:
            scored_songs.append((song, score, explanation))
    # key=lambda item: item[1] means “when sorting, use the score”
    ranked = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    return ranked[:k]


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Compute one song's score and the reasons for that score."""
    score = 0.0
    reasons = []
    if song["mood"] == user_prefs["mood"]:
        score += 3.0
        reasons.append("mood match (+3.0)")
    if song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append("genre match (+2.0)")

    energy_similarity = 1 - abs(song["energy"] - user_prefs["energy"])
    energy_points = 2.0 * energy_similarity
    score += energy_points
    # What :.2f means:
    # f = format as a floating-point number
    # .2 = show 2 digits after the decimal point
    reasons.append(f"energy similarity (+{energy_points: .2f})")

    acoustic_similarity = 1 - abs(song["acousticness"] - user_prefs["acousticness"])
    acoustic_points = 1.0 * acoustic_similarity
    score += acoustic_points
    reasons.append(f"acoustic similarity (+{acoustic_points: .2f})")

    valence_similarity = 1 - abs(song["valence"] - user_prefs["valence"])
    valence_points = 0.5 * valence_similarity
    score += valence_points
    reasons.append(f"valence similarity (+{valence_points: .2f})")
    return score, reasons
