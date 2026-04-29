# Model Card: Music RAG Reliability Benchmark

## Model/System Name

**Music RAG Reliability Benchmark**

## Intended Use

This system recommends music tracks from a Spotify-style dataset and explains why each track was retrieved. It is intended as a classroom applied AI system, not a production recommender.

The system is useful for demonstrating:

- offline retrieval over structured music features
- grounded explanation generation
- optional Gemini wording
- guardrails and deterministic fallback
- reliability evaluation metrics

## Base Project

The base project was **Music Recommender Simulation**, an 18-song mood-based recommender. It ranked songs using a weighted scoring rule over mood, genre, energy, acousticness, and valence.

The original project was explainable but small. This final version keeps that baseline and adds a real-data RAG-style path with 500 sampled tracks, evidence-based retrieval, LLM explanation validation, and reliability metrics.

## How It Works

1. Load tracks from `data/spotify_tracks_sample_500.csv`.
2. Convert rows into normalized `TrackRecord` objects.
3. Retrieve top tracks using genre and audio-feature similarity.
4. Carry evidence strings forward from retrieval.
5. Generate deterministic explanations or optional Gemini explanations.
6. Run guardrails against explanation text and evidence.
7. Use deterministic fallback when Gemini output is malformed or unsupported.
8. Evaluate reliability with predefined benchmark queries.

## Data

The real-data path uses a deterministic 500-row sample from the Hugging Face Spotify Tracks Dataset. The sample includes track name, artists, album name, genre, popularity, danceability, energy, acousticness, valence, and tempo.

The dataset does not include lyrics, vocals, user listening history, reviews, or cultural context. For that reason, explanations are not allowed to claim anything about lyrics, vocals, fan popularity, live performance, or awards.

## Reliability Evaluation

Current verified automated test result:

```text
42 passed
```

The evaluator runs three predefined retrieval cases and reports:

- unsupported claim rate
- fallback rate
- format failure rate
- global evidence coverage

Current evaluator demo output:

```text
Unsupported claim rate: 0.33
Fallback rate: 0.67
Format failure rate: 0.33
Global evidence coverage: 1.00
```

This shows that unsafe raw LLM-style output is detected and replaced, while final explanations preserve evidence coverage.

## Guardrails

Guardrails check for:

- empty explanations
- unsupported claims such as lyrics, vocals, fan favorite, chart-topping, or live performance
- missing retrieval evidence
- incomplete evidence fields

Error-level violations trigger fallback. Warning-level violations are measured but do not trigger fallback.

## Limitations and Bias

The system may overvalue numeric audio-feature similarity because it does not know the listener's full context. It also depends on the dataset's genre labels and Spotify-style features, which may not represent all cultures, languages, genres, or listening situations equally.

The system should not be used to make claims about lyrical meaning, vocal quality, popularity, or cultural significance because those fields are not available in the evidence.

## Misuse Risks

The main misuse risk is presenting generated explanations as if they know more than the dataset supports. The guardrails reduce this risk by rejecting unsupported claims and falling back to deterministic explanations.

## AI Collaboration Reflection

I used AI to help reason through system architecture, test design, guardrails, and deadline tradeoffs. A helpful suggestion was to preserve the original recommender separately from the real-data RAG path, which made the extension easier to explain.

A flawed suggestion was to spend time tightening explanation wording before the evaluator and CLI were complete. That would have improved polish, but it was not the highest-value move for the rubric. I adjusted by prioritizing the evaluator, trace command, and documentation needed to prove reliability.

## Future Improvements

- Add more diverse benchmark queries.
- Add a small human evaluation form for explanation quality.
- Compare deterministic explanations against live Gemini outputs when an API key is available.
- Add diversity-aware retrieval so top recommendations are not too similar.
- Add richer metadata sources if lyrics, release era, or artist context become available.
