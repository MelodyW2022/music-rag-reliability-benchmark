# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version of the project simulates a simple content-based music recommender that suggests songs based on a user's preferred vibe. It compares each song to a user taste profile using weighted features such as mood, genre, and energy, then ranks songs by how closely they match. The system is designed to be easy to explain, so each recommendation can be traced back to the features that contributed most to its score.

---

## How The System Works

What features does each `Song` use in your system?

Each song uses both category labels and numerical audio features. The main features are `genre`, `mood`, `energy`, `acousticness`, and `valence`. I treat mood as the main signal for vibe, genre as the style signal, energy as the intensity signal, acousticness as the organic versus electronic texture signal, and valence as the emotional positivity signal.

What information does your `UserProfile` store?

The user profile stores the user's preferred genre, preferred mood, and target values for the numerical vibe features I chose to use, especially energy, acousticness, and valence. These preferences create a simple taste profile that the recommender can compare against each song in the catalog.

How does your `Recommender` compute a score for each song?

The recommender uses a weighted scoring rule. My finalized algorithm recipe is:

- `+3.0` points if the song's mood matches the user's favorite mood
- `+2.0` points if the song's genre matches the user's favorite genre
- `+2.0 * (1 - abs(song.energy - user.target_energy))`
- `+1.0 * (1 - abs(song.acousticness - user.target_acousticness))`
- `+0.5 * (1 - abs(song.valence - user.target_valence))`

This recipe makes mood the strongest signal because the project is centered on matching a listener's vibe. Genre still matters, but it acts more like a style preference. For numerical features like energy, acousticness, and valence, the system rewards songs that are closer to the user's target values instead of simply favoring higher numbers.

How do you choose which songs to recommend?

After scoring every song, the recommender ranks the songs from highest score to lowest score. It then returns the top `k` songs as the recommendations. This means the system first uses a scoring rule to judge one song at a time, then uses a ranking rule to choose the best overall list.

What biases or limitations do you expect from this system?

This system might over-prioritize mood and genre labels, which could cause it to miss songs from other genres that still match the user's overall vibe. It may also favor songs that are close to the chosen numerical targets and ignore other important qualities, such as lyrics, vocals, cultural context, or songs that blend multiple moods at once.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

3. Run the app:

```bash
python3 -m src.main
```

### Running Tests

Run the starter tests with:

```bash
python3 -m pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

I tested the system's sensitivity by doubling the weight on energy, changing the energy similarity contribution from `2.0 * similarity` to `4.0 * similarity`. This made the recommender much more intensity-focused. Across profiles like `high_energy_pop`, `deep_intense_rock`, and `conflicting_vibe`, songs with similar energy levels rose in the rankings even when they did not match the user's preferred genre. The clearest example was the `peaceful_punk` profile, where calm low-energy songs outranked the actual punk track because their energy values were much closer to the user's target.

This change made the recommendations different more than it made them more accurate. In some cases it improved the vibe match by surfacing songs with a similar intensity, but it also made the system drift away from the user's stated style preferences. Overall, the experiment showed that energy is a powerful feature, but if it is weighted too heavily, the recommender becomes less genre-aware and less precise.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods

Yes. Because the model is mood-first, songs that do not match the user's preferred mood can be pushed down even if they are still a good fit in other ways. The small dataset also means some genres and moods have only one song, so those styles have fewer chances to appear in recommendations.

- Does it treat all users as if they have the same taste shape

Yes. The system assumes every user can be described by one favorite mood, one favorite genre, and one target value for features like energy, acousticness, and valence. Real listeners usually have more flexible tastes that change by time, activity, or context, so this model oversimplifies user preference.

- Is it biased toward high energy or one genre by default

Not by default. In its current version, the model is mainly biased toward mood because mood receives the largest bonus in the scoring rule. Genre and energy still matter, but they act as secondary signals, so the system is more likely to favor songs that match the user's main mood than songs from one specific genre or energy level.

- How could this be unfair if used in a real product

In a real product, this could make recommendations feel narrow or repetitive, especially for users with mixed or unusual tastes. It could also reduce visibility for less represented genres, moods, or artists because the system keeps rewarding the same kinds of matches instead of encouraging diversity or discovery.

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"
