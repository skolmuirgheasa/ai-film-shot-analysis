import numpy as np
import pandas as pd
import scipy.stats as stats

def generate_hollywood_shot_data(n_movies=1000):
    """
    Generates a synthetic dataset of movie shot lengths that mimics 
    real Hollywood statistics (Log-Normal distribution).
    
    Data based on Cinemetrics.lv and MovieNet insights:
    - Action movies: Mode ~2.0s, Median ~2.5s
    - Drama/General: Mode ~3.0s, Median ~4.0s
    - Tail extends to long shots, but mass is < 5s.
    """
    
    np.random.seed(42)
    
    movies_data = []
    
    # Modern Action / Blockbuster Profile (The "John Wick" / "Mad Max" style)
    # Mode at 2.5s, heavy skew
    # Log-Normal params: mu (scale), sigma (shape)
    # For log-normal: mode = exp(mu - sigma^2), median = exp(mu)
    
    # Let's generate shots for 500 "Action/Thriller" movies
    for i in range(500):
        # Vary the median ASL slightly per movie (2.0s to 3.5s range for action)
        movie_median = np.random.uniform(2.0, 3.5)
        sigma = 0.8  # Shape parameter controlling the tail
        mu = np.log(movie_median)
        
        # Generate 2000 shots per movie (approx 90-100 mins)
        shots = np.random.lognormal(mean=mu, sigma=sigma, size=2500)
        
        # Filter realistic outliers (shots < 0.2s or > 60s are rare but exist)
        shots = shots[(shots > 0.5) & (shots < 120)]
        
        movies_data.append({
            "movie_id": f"action_{i}",
            "genre": "Action/Thriller",
            "year": np.random.randint(2020, 2026),
            "shots": shots,
            "avg_shot_length": np.mean(shots),
            "median_shot_length": np.median(shots)
        })

    # Generate 500 "Drama/Indie" movies (Slightly longer shots)
    for i in range(500):
        # Median ASL 4.0s to 7.0s
        movie_median = np.random.uniform(4.0, 7.0)
        sigma = 0.9
        mu = np.log(movie_median)
        
        shots = np.random.lognormal(mean=mu, sigma=sigma, size=1500)
        shots = shots[(shots > 0.5) & (shots < 180)]
        
        movies_data.append({
            "movie_id": f"drama_{i}",
            "genre": "Drama/Indie",
            "year": np.random.randint(2020, 2026),
            "shots": shots,
            "avg_shot_length": np.mean(shots),
            "median_shot_length": np.median(shots)
        })

    # Flatten into a DataFrame of ALL shots for the histogram
    all_shots = []
    for m in movies_data:
        for s in m["shots"]:
            all_shots.append({
                "movie_id": m["movie_id"],
                "genre": m["genre"],
                "shot_length_sec": round(s, 2)
            })
            
    df_shots = pd.DataFrame(all_shots)
    df_movies = pd.DataFrame(movies_data).drop(columns=["shots"])
    
    return df_shots, df_movies

if __name__ == "__main__":
    print("Generating synthetic MovieNet-like dataset...")
    df_shots, df_movies = generate_hollywood_shot_data()
    
    df_shots.to_csv("analysis/data/all_shots.csv", index=False)
    df_movies.to_csv("analysis/data/movie_stats.csv", index=False)
    
    print(f"Generated {len(df_shots)} shots from {len(df_movies)} movies.")
    print(f"Global Median Shot Length: {df_shots['shot_length_sec'].median():.2f}s")
    print("Data saved to analysis/data/")

