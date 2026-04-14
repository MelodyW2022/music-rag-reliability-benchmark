# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**VibeMatch 1.0**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  

This recommender generates a short ranked list of songs from a small catalog based on a user's preferred vibe. It is designed to recommend songs that are close to the user's mood, genre, and numeric feature targets.

- What assumptions does it make about the user  

It assumes a user can be represented by one main mood, one favorite genre, and target values for energy, acousticness, and valence. It also assumes that songs with similar feature values will feel like good recommendations.

- Is this for real users or classroom exploration  

This system is for classroom exploration, not for real users. Its main purpose is to show how a simple recommender can turn user preferences and song features into ranked outputs.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  

Each song uses `genre`, `mood`, `energy`, `acousticness`, and `valence` as the main recommendation features. I treat mood as the strongest signal for vibe, while genre, energy, acousticness, and valence help refine the match.

- What user preferences are considered  

The model considers the user's preferred genre, preferred mood, target energy, target acousticness, and target valence. These values create a simple taste profile that can be compared against every song in the catalog.

- How does the model turn those into a score  

The model gives a large bonus when a song matches the user's preferred mood and a smaller bonus when it matches the preferred genre. Then it adds similarity points for how close the song is to the user's target energy, acousticness, and valence values. Songs with higher total scores are ranked higher in the recommendation list.

- What changes did you make from the starter logic  

I changed the starter logic by adding a real scoring rule, explanation strings, multiple user profiles for testing, and more songs in the dataset. I also made the system reward similarity on numeric features instead of just checking exact matches.

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  

The catalog currently contains 18 songs in `data/songs.csv`.

- What genres or moods are represented  

The dataset includes genres such as pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, edm, r&b, country, punk, classical, hip-hop, and dream pop. The moods include happy, chill, intense, relaxed, moody, focused, nostalgic, excited, romantic, hopeful, rebellious, peaceful, confident, and ethereal.

- Did you add or remove data  

Yes. I added 8 new songs to the starter dataset to make the catalog more diverse and to test the recommender on a wider range of genres and moods.

- Are there parts of musical taste missing in the dataset  

Yes. The dataset is still very small and does not include lyrics, language, artist popularity, era, instrumentation details, or more complex emotional categories. It also does not cover every genre or listening context that real users might care about.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  

The system works best for users with clear and focused preferences, such as `high_energy_pop`, `chill_lofi`, or `deep_intense_rock`. It performs well when the user's taste can be described by one strong mood and a few matching numeric feature targets.

- Any patterns you think your scoring captures correctly  

I think the scoring captures overall vibe fairly well, especially the difference between calm and energetic songs. It also does a good job finding songs that are close in mood and still flexible enough to surface related songs from nearby genres when the numeric features are similar.

- Cases where the recommendations matched your intuition  

The recommendations matched my intuition most clearly for the `chill_lofi` and `deep_intense_rock` profiles. For example, `Library Rain` and `Midnight Coding` rose to the top for `chill_lofi`, while `Storm Runner` ranked first for `deep_intense_rock`, which felt correct based on the features in the dataset.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  

The recommender does not consider lyrics, language, vocals, cultural meaning, or personal memories connected to a song. It only uses the structured features in the CSV, so it misses many reasons why a listener might actually like or dislike a track.

- Genres or moods that are underrepresented  

Some genres and moods are underrepresented because the catalog is small and several categories appear only once. That means the system has fewer chances to recommend those styles, even when a user might enjoy them.

- Cases where the system overfits to one preference  

Because the model is mood-first, it can overfit to the user's preferred mood and push down songs that differ in mood but still match the user's taste in other ways. The numeric features can also create a narrow vibe bubble where songs with similar energy, acousticness, and valence keep appearing repeatedly.

- Ways the scoring might unintentionally favor some users  

The scoring may unintentionally favor users whose tastes fit neatly into one main mood, one genre, and a few target feature values. Users with mixed, changing, or less represented tastes may get weaker recommendations because the model assumes everyone has the same general taste shape.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  

I tested five user profiles: `high_energy_pop`, `chill_lofi`, `deep_intense_rock`, `conflicting_vibe`, and `peaceful_punk`. These profiles gave me a mix of normal listening preferences and adversarial cases with conflicting signals.

- What you looked for in the recommendations  

I looked at whether the top songs matched the intended vibe, not just the exact genre or mood labels. I also checked whether the explanation strings made sense and whether songs with similar energy, acousticness, and valence were being ranked in a reasonable order.

- What surprised you  

What surprised me most was how often songs from other genres still appeared when their numeric features were close to the target. A good example is `Gym Hero`, which kept showing up for profiles that wanted intensity or upbeat energy even when the genre was not the main match. This made sense after I looked at the explanation strings, because the song often scored well on energy and other vibe features.

- Any simple tests or comparisons you ran  

I compared the results across all five profiles and wrote down how the top recommendations changed. I also ran a sensitivity test by temporarily doubling the energy weight from `2.0` to `4.0` and then comparing the rankings before and after the change. That test showed that the system became more intensity-focused and less genre-aware, which helped confirm that my current baseline model is mainly mood-first, with genre and energy acting as secondary signals.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  

I would add more features such as tempo ranges, lyric themes, release era, and whether a song feels more electronic or live. I would also allow users to express broader preferences instead of only one favorite mood and one favorite genre.

- Better ways to explain recommendations  

I would improve the explanations by making them more natural and user-friendly, such as saying a song was recommended because it is "calm and acoustic" instead of only listing score components. That would make the reasoning easier for non-programmers to understand.

- Improving diversity among the top results  

I would add a diversity rule so the top results are not all near-duplicates of the same vibe. This could help the recommender suggest songs from different but still relevant genres or moods.

- Handling more complex user tastes  

I would let the model support multiple moods, multiple favorite genres, or changing preferences based on context, like studying, working out, or relaxing. That would better reflect how real people listen to music.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  

I learned that recommender systems are really built from small design choices that add up. Even a simple scoring rule can strongly shape what a user sees, which made recommendation results feel much less mysterious to me.

- Something unexpected or interesting you discovered  

One interesting thing I discovered was how often a song like `Gym Hero` kept showing up for very different profiles. At first that felt surprising, but it made sense once I saw how strongly the numeric vibe features could support a song even when the genre was not a perfect match.

- How this changed the way you think about music recommendation apps  

This project made me think of music recommendation apps as systems that are always balancing tradeoffs between accuracy, simplicity, and diversity. It also showed me that human judgment still matters because a model can find mathematically similar songs without fully understanding what the listener actually meant.
