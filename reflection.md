# Reflection Comparisons

This section helps me compare how the recommender responds to different user profiles. The goal is not just to list different outputs, but to explain what changed in the rankings and why those changes make sense based on the scoring rule. Looking at the profiles side by side helps me check whether the recommender is actually reacting to mood, genre, energy, acousticness, and valence the way I intended.

Questions to keep in mind while reading these comparisons:

- Which songs stayed the same across two profiles, and why?
- Which songs moved up or down, and which feature likely caused that shift?
- Did the output change in a way that matches the user preferences?
- Did the recommender behave sensibly, or did it reveal a weakness or bias?

- `high_energy_pop` vs `chill_lofi`: The pop profile favored upbeat songs like `Sunrise City`, while the lofi profile shifted toward quieter songs like `Library Rain` and `Midnight Coding`. This makes sense because the two profiles ask for opposite energy levels and very different acoustic textures.

- `high_energy_pop` vs `deep_intense_rock`: Both profiles liked high-energy songs, but the pop profile leaned brighter and happier while the rock profile leaned harder and more intense. That is why songs like `Gym Hero` can appear in both lists, but `Storm Runner` fits the rock profile more naturally.

- `high_energy_pop` vs `conflicting_vibe`: Both profiles still pulled in energetic songs, but the conflicting profile let moodier tracks like `Night Drive Loop` rise because it asked for a darker mood. This shows that high energy does not always mean cheerful.

- `high_energy_pop` vs `peaceful_punk`: The pop profile rewarded bright, upbeat songs, while the peaceful punk profile moved toward calm and low-energy songs like `Cathedral Echoes`. The outputs changed because one profile asks for excitement and the other asks for calm, even though both include a genre preference.

- `chill_lofi` vs `deep_intense_rock`: The chill lofi profile favored soft, study-style tracks, while the deep intense rock profile favored loud, forceful songs like `Storm Runner`. This difference makes sense because the model is responding to opposite mood and energy goals.

- `chill_lofi` vs `conflicting_vibe`: The lofi profile produced calm, acoustic recommendations, while the conflicting profile mixed moody and high-energy songs. This makes sense because the second profile contains signals that pull in different directions.

- `chill_lofi` vs `peaceful_punk`: Both profiles liked lower-energy songs, so they shared some mellow recommendations. The difference is that `chill_lofi` still favored lofi label matches, while `peaceful_punk` showed how the system can drift away from genre when the peaceful mood and low energy are much stronger clues.

- `deep_intense_rock` vs `conflicting_vibe`: Both profiles included intense or high-energy songs, but the conflicting profile let darker or moodier tracks rank higher because of the mood target. This shows that the model can separate “powerful” from “happy,” even when both profiles want energy.

- `deep_intense_rock` vs `peaceful_punk`: These two profiles produced almost opposite outputs. The rock profile favored forceful, high-energy tracks, while the peaceful punk profile favored quiet, acoustic songs, which shows the energy target strongly changes the ranking.

- `conflicting_vibe` vs `peaceful_punk`: The conflicting profile still pushed high-energy songs upward, while the peaceful punk profile rewarded calm songs with low energy and high acousticness. This makes sense because one profile is internally tense and dramatic, while the other asks for calm even though its genre label points another way.
