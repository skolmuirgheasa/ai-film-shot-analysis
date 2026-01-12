
# Analysis Report: Real Hollywood Data
    
## The "Max Shot" Myth
We analyzed 3681 shots from 4 critical masterpieces (*Mad Max: Fury Road*, *Bourne Ultimatum*, *Run Lola Run*, *Moulin Rouge!*).

### Key Statistics
| Movie | Median Shot (s) | Max Shot (s) | 95% of Shots Under (s) |
|-------|----------------|--------------|------------------------|
| Mad Max: Fury Road | 1.70s | 32.9s | 7.5s |
| Moulin Rouge! | 1.10s | 78.0s | 3.5s |
| Run Lola Run | 2.10s | 58.8s | 10.0s |
| The Bourne Ultimatum | 1.60s | 19.7s | 5.5s |

### Insight
Even in these high-octane films, the **maximum** shot length rarely exceeds 1 minute, and the vast majority (95%) are under 10 seconds.
*The Bourne Ultimatum* constitutes a masterpiece of action cinema, yet its **longest single shot is only 19.7 seconds**.

This proves that AI video models should prioritize **inter-shot consistency** (character identity across cuts) rather than trying to generate minute-long continuous takes.
