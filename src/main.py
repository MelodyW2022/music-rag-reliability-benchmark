"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # multiple test profiles
    profiles = {
        "high_energy_pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "acousticness": 0.2,
            "valence": 0.9,
        },
        "chill_lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "acousticness": 0.82,
            "valence": 0.60,
        },
        "deep_intense_rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.90,
            "acousticness": 0.10,
            "valence": 0.45,
        },
        "conflicting_vibe": {
            "genre": "pop",
            "mood": "moody",
            "energy": 0.92,
            "acousticness": 0.10,
            "valence": 0.20,
        },
        "peaceful_punk": {
            "genre": "punk",
            "mood": "peaceful",
            "energy": 0.20,
            "acousticness": 0.90,
            "valence": 0.65,
        },
    }
    for name, user_prefs in profiles.items():

        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(
            f"####################Top 5 Recommendations for {name}####################"
        )

        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


# It’s important because importing a file is usually meant to reuse its functions, not accidentally run the whole program.
if __name__ == "__main__":
    main()
