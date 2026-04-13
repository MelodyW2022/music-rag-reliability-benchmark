import csv
from re import S
from typing import List, Dict, Tuple, Optional
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
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # Implement CSV loading logic
    print(f"Loading songs from {csv_path}...")
    songs = []

    """open the file safely
      "with" automatically closes it afterwards
      newline="" is the recommended way when using csv, it means don't pre-process newline characters in a special way and let the csv module interpret rows properly
      encoding="utf-8" is a safe default
    """

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
       # reader is an interator over rows and each row is a dict with keys from the header
       reader = csv.DictReader(csvfile)
       for row in reader:
           song = {
               "id" : int(row["id"])   ,
                "title" : row["title"],
                "artist" : row["artist"],
                "genre" : row["genre"],
                "mood" : row["mood"],
                "energy" : float(row["energy"]),
                "tempo_bpm" : float(row["tempo_bpm"]),
                "valence" : float(row["valence"]),
                "danceability" : float(row["danceability"]),
                "acousticness" : float(row["acousticness"])
           }
           songs.append(song)


    return songs
    
def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
