# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

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
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
