# Notes for Personal Use

## Key Decisions

- Why I chose this implementation in the end

I chose a mood-first recommender with genre, energy, acousticness, and valence as supporting features because it matched how I wanted to define musical vibe. This design was simple enough to explain clearly, but still flexible enough to surface songs that were close in feel even across genres.

- What other options I considered

I considered making the system more genre-first or more energy-focused. I also experimented with temporarily doubling the energy weight to see how much that changed the ranking behavior.

- Why this solution worked better

The final version worked better because it balanced exact category matches with numeric similarity. It could still recommend nearby-vibe songs without completely ignoring the user's preferred mood.

## Pitfalls / Bugs

- What issue or bug I ran into

One issue I ran into was that my numeric similarity features did not seem to affect the score at first. I also hit import problems when trying to run `python3 -m src.main`.

- Why it happened

The numeric scoring bug happened because I was checking for exact equality on values like energy instead of always calculating similarity. The import bug happened because `src/main.py` originally used a top-level import instead of a package-relative import.

- How I fixed it

I fixed the scoring bug by removing the equality checks and always computing similarity with expressions like `1 - abs(song["energy"] - user_prefs["energy"])`. I fixed the import bug by changing the import in `src/main.py` to `from .recommender import ...`.

- What I should remember next time

Next time I should remember that categorical features and numeric features need different logic. Exact-match checks work for mood or genre, but numeric features should usually use closeness instead of equality.

## Reusable Snippets

- Code patterns or ideas I can reuse in future projects

I can reuse the pattern of scoring one item, storing both the numeric score and explanation reasons, and then sorting the full list. I can also reuse the idea of testing multiple user profiles to stress-test a recommender.

- Small templates, common logic, or useful structures

Useful structures from this project include `score = 0.0`, `reasons = []`, similarity formulas like `1 - abs(a - b)`, and `sorted(items, key=lambda item: item[1], reverse=True)` for ranking.

## One-Sentence Learnings

- One sentence that helps me quickly remember the key idea later
- Example: "Cleanup means canceling the old task and keeping only the latest one."

Recommenders feel smart, but they are really the result of simple scoring choices that strongly shape what users see.

## If I Redo This Project

- What I would do differently next time

If I redo this project, I would plan the user profiles and scoring features earlier so the code, README, and model card stay aligned from the start. I would also clean up notes and experiment results as I go instead of leaving them all for the end.

- How I could finish the project faster or with fewer mistakes

I could finish faster by testing one small feature at a time, running the app after each change, and writing shorter helper functions earlier. I would also decide on the final file structure sooner so I do not duplicate answers across `README.md`, `model_card.md`, and notes.

##Before Energy change from 2.0 to 4.0

```
####################Top 5 Recommendations for high_energy_pop####################
Sunrise City - Score: 8.41
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 1.96), acoustic similarity (+ 0.98), valence similarity (+ 0.47)

Rooftop Lights - Score: 6.22
Because: mood match (+3.0), energy similarity (+ 1.92), acoustic similarity (+ 0.85), valence similarity (+ 0.46)

Gym Hero - Score: 5.02
Because: genre match (+2.0), energy similarity (+ 1.74), acoustic similarity (+ 0.85), valence similarity (+ 0.43)

Bassline Mirage - Score: 3.28
Because: energy similarity (+ 1.96), acoustic similarity (+ 0.94), valence similarity (+ 0.38)

Night Drive Loop - Score: 3.17
Because: energy similarity (+ 1.90), acoustic similarity (+ 0.98), valence similarity (+ 0.29)

####################Top 5 Recommendations for chill_lofi####################
Library Rain - Score: 8.46
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 2.00), acoustic similarity (+ 0.96), valence similarity (+ 0.50)

Midnight Coding - Score: 8.23
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 1.86), acoustic similarity (+ 0.89), valence similarity (+ 0.48)

Spacewalk Thoughts - Score: 6.23
Because: mood match (+3.0), energy similarity (+ 1.86), acoustic similarity (+ 0.90), valence similarity (+ 0.47)

Focus Flow - Score: 5.36
Because: genre match (+2.0), energy similarity (+ 1.90), acoustic similarity (+ 0.96), valence similarity (+ 0.49)

Coffee Shop Stories - Score: 3.33
Because: energy similarity (+ 1.96), acoustic similarity (+ 0.93), valence similarity (+ 0.45)

####################Top 5 Recommendations for deep_intense_rock####################
Storm Runner - Score: 8.46
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 1.98), acoustic similarity (+ 1.00), valence similarity (+ 0.48)

Gym Hero - Score: 6.23
Because: mood match (+3.0), energy similarity (+ 1.94), acoustic similarity (+ 0.95), valence similarity (+ 0.34)

Static Hearts - Score: 3.41
Because: energy similarity (+ 1.98), acoustic similarity (+ 0.98), valence similarity (+ 0.45)

Neon Parade - Score: 3.13
Because: energy similarity (+ 1.90), acoustic similarity (+ 0.94), valence similarity (+ 0.30)

Bassline Mirage - Score: 3.11
Because: energy similarity (+ 1.76), acoustic similarity (+ 0.96), valence similarity (+ 0.40)

####################Top 5 Recommendations for conflicting_vibe####################
Night Drive Loop - Score: 5.89
Because: mood match (+3.0), energy similarity (+ 1.66), acoustic similarity (+ 0.88), valence similarity (+ 0.35)

Gym Hero - Score: 5.14
Because: genre match (+2.0), energy similarity (+ 1.98), acoustic similarity (+ 0.95), valence similarity (+ 0.21)

Sunrise City - Score: 4.90
Because: genre match (+2.0), energy similarity (+ 1.80), acoustic similarity (+ 0.92), valence similarity (+ 0.18)

Storm Runner - Score: 3.34
Because: energy similarity (+ 1.98), acoustic similarity (+ 1.00), valence similarity (+ 0.36)

Static Hearts - Score: 3.25
Because: energy similarity (+ 1.94), acoustic similarity (+ 0.98), valence similarity (+ 0.32)

####################Top 5 Recommendations for peaceful_punk####################
Cathedral Echoes - Score: 6.38
Because: mood match (+3.0), energy similarity (+ 1.96), acoustic similarity (+ 0.93), valence similarity (+ 0.48)

Spacewalk Thoughts - Score: 3.32
Because: energy similarity (+ 1.84), acoustic similarity (+ 0.98), valence similarity (+ 0.50)

Static Hearts - Score: 3.29
Because: genre match (+2.0), energy similarity (+ 0.62), acoustic similarity (+ 0.22), valence similarity (+ 0.45)

Library Rain - Score: 3.14
Because: energy similarity (+ 1.70), acoustic similarity (+ 0.96), valence similarity (+ 0.47)

Coffee Shop Stories - Score: 3.12
Because: energy similarity (+ 1.66), acoustic similarity (+ 0.99), valence similarity (+ 0.47)
```

##After Energy change from 2.0 to 4.0

```
####################Top 5 Recommendations for high_energy_pop####################
Sunrise City - Score: 10.37
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 3.92), acoustic similarity (+ 0.98), valence similarity (+ 0.47)

Rooftop Lights - Score: 8.14
Because: mood match (+3.0), energy similarity (+ 3.84), acoustic similarity (+ 0.85), valence similarity (+ 0.46)

Gym Hero - Score: 6.76
Because: genre match (+2.0), energy similarity (+ 3.48), acoustic similarity (+ 0.85), valence similarity (+ 0.43)

Bassline Mirage - Score: 5.24
Because: energy similarity (+ 3.92), acoustic similarity (+ 0.94), valence similarity (+ 0.38)

Night Drive Loop - Score: 5.07
Because: energy similarity (+ 3.80), acoustic similarity (+ 0.98), valence similarity (+ 0.29)

####################Top 5 Recommendations for chill_lofi####################
Library Rain - Score: 10.46
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 4.00), acoustic similarity (+ 0.96), valence similarity (+ 0.50)

Midnight Coding - Score: 10.09
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 3.72), acoustic similarity (+ 0.89), valence similarity (+ 0.48)

Spacewalk Thoughts - Score: 8.10
Because: mood match (+3.0), energy similarity (+ 3.72), acoustic similarity (+ 0.90), valence similarity (+ 0.47)

Focus Flow - Score: 7.25
Because: genre match (+2.0), energy similarity (+ 3.80), acoustic similarity (+ 0.96), valence similarity (+ 0.49)

Coffee Shop Stories - Score: 5.29
Because: energy similarity (+ 3.92), acoustic similarity (+ 0.93), valence similarity (+ 0.45)

####################Top 5 Recommendations for deep_intense_rock####################
Storm Runner - Score: 10.45
Because: mood match (+3.0), genre match (+2.0), energy similarity (+ 3.96), acoustic similarity (+ 1.00), valence similarity (+ 0.48)

Gym Hero - Score: 8.17
Because: mood match (+3.0), energy similarity (+ 3.88), acoustic similarity (+ 0.95), valence similarity (+ 0.34)

Static Hearts - Score: 5.39
Because: energy similarity (+ 3.96), acoustic similarity (+ 0.98), valence similarity (+ 0.45)

Neon Parade - Score: 5.04
Because: energy similarity (+ 3.80), acoustic similarity (+ 0.94), valence similarity (+ 0.30)

Sunrise City - Score: 4.90
Because: energy similarity (+ 3.68), acoustic similarity (+ 0.92), valence similarity (+ 0.31)

####################Top 5 Recommendations for conflicting_vibe####################
Night Drive Loop - Score: 7.55
Because: mood match (+3.0), energy similarity (+ 3.32), acoustic similarity (+ 0.88), valence similarity (+ 0.35)

Gym Hero - Score: 7.12
Because: genre match (+2.0), energy similarity (+ 3.96), acoustic similarity (+ 0.95), valence similarity (+ 0.21)

Sunrise City - Score: 6.70
Because: genre match (+2.0), energy similarity (+ 3.60), acoustic similarity (+ 0.92), valence similarity (+ 0.18)

Storm Runner - Score: 5.32
Because: energy similarity (+ 3.96), acoustic similarity (+ 1.00), valence similarity (+ 0.36)

Static Hearts - Score: 5.18
Because: energy similarity (+ 3.88), acoustic similarity (+ 0.98), valence similarity (+ 0.32)

####################Top 5 Recommendations for peaceful_punk####################
Cathedral Echoes - Score: 8.33
Because: mood match (+3.0), energy similarity (+ 3.92), acoustic similarity (+ 0.93), valence similarity (+ 0.48)

Spacewalk Thoughts - Score: 5.16
Because: energy similarity (+ 3.68), acoustic similarity (+ 0.98), valence similarity (+ 0.50)

Library Rain - Score: 4.83
Because: energy similarity (+ 3.40), acoustic similarity (+ 0.96), valence similarity (+ 0.47)

Coffee Shop Stories - Score: 4.78
Because: energy similarity (+ 3.32), acoustic similarity (+ 0.99), valence similarity (+ 0.47)

Focus Flow - Score: 4.55
Because: energy similarity (+ 3.20), acoustic similarity (+ 0.88), valence similarity (+ 0.47)
```
