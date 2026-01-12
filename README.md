# AI Film Shot Analysis: The Consistency Gap

**A data-driven analysis of modern cinema challenging the current "Long Duration" AI Video roadmap.**

![Max Shot Lengths](docs/images/real_max_shots.png)

## Executive Summary

Current AI Video Models (Google Veo, OpenAI Sora, Runway Gen-3) are heavily optimizing for **Long Duration Coherence** (generating 60s+ continuous clips).

However, our analysis of **3,600+ real shots** from four cinematic masterpieces (*Mad Max: Fury Road*, *The Bourne Ultimatum*, *Run Lola Run*, *Moulin Rouge!*) reveals that this goal is misaligned with professional filmmaking reality.

**The Reality: Filmmakers don't need "One Long Shot." They need "Many Consistent Short Shots."**

![Shot Length Distribution](docs/images/real_histogram.png)

## Key Findings

### 1. The "Max Shot" Myth
The most striking finding is not just the low Average Shot Length (ASL), but the extremely low **Maximum Shot Length**.

| Movie | Median Shot | **Max Shot** | 95% of Shots Under |
|-------|-------------|--------------|--------------------|
| **The Bourne Ultimatum** | **1.6s** | **19.7s** | **5.5s** |
| **Mad Max: Fury Road** | 1.7s | 32.9s | 7.5s |
| **Moulin Rouge!** | 1.1s | 78.0s | 3.5s |
| **Run Lola Run** | 2.1s | 58.8s | 10.0s |

**Insight:** *The Bourne Ultimatum*, a genre-defining action film, has a **maximum shot length of only 19.7 seconds**. The entire film is constructed without a single "long take" that current AI models are striving to generate.

### 2. The 5-Second Threshold
**95% of shots in *The Bourne Ultimatum* are shorter than 5.5 seconds.**

Most current AI research focuses on extending generation to 60+ seconds. Yet, for this style of filmmaking, **95% of that compute is wasted on duration that will never be used.** The real challenge is not duration, but **consistency** across the hundreds of 2-second cuts.

![CDF](docs/images/real_cdf.png)

## The Conclusion

The roadmap for AI Video should pivot from **Duration Extension** to **Inter-Shot Consistency**.

*   **Current Goal:** Generate 1 minute of video where the character doesn't morph.
*   **Real Need:** Generate twenty 3-second clips where the character looks identical across all of them.

## Methodology & Reproduction

This analysis is based on raw shot-by-shot data extracted from the [Cinemetrics Database](https://cinemetrics.uchicago.edu/).

### 1. Install Dependencies
```bash
pip install -r analysis/requirements.txt
```

### 2. Fetch & Parse Data
We use a custom parser to extract raw shot data from Cinemetrics logs for the target films.
```bash
python analysis/parse_cinemetrics.py
```
*This generates `analysis/data/real_shots.csv` containing frame-accurate shot lengths.*

### 3. Run Analysis
```bash
python analysis/analyze_shots.py
```
*This produces the charts and statistics found in this README.*

## Data Sources
*   **Cinemetrics**: [https://cinemetrics.uchicago.edu/](https://cinemetrics.uchicago.edu/)
*   **Mad Max: Fury Road** (Data submitted by Yvonne Festl)
*   **The Bourne Ultimatum** (Data submitted by Erik)
*   **Run Lola Run** (Data submitted by Sari Bouweester)
*   **Moulin Rouge!** (Data submitted by Matt Harris)
