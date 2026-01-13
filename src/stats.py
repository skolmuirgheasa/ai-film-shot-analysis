import pandas as pd
import numpy as np

def load_data():
    """Loads and standardizes datasets."""
    try:
        hero_df = pd.read_csv("data/hero_movies_clean.csv")
    except FileNotFoundError:
        hero_df = pd.DataFrame()
        
    try:
        mb_df = pd.read_csv("data/moviebench_raw.csv")
        # Ensure clean titles immediately
        if not mb_df.empty:
            mb_df['clean_title'] = mb_df['movie_title'].apply(clean_mb_title)
    except FileNotFoundError:
        mb_df = pd.DataFrame()
        
    return hero_df, mb_df

def clean_mb_title(t):
    """Helper to clean MovieBench titles."""
    parts = t.split('_', 1)
    if len(parts) > 1 and parts[0].isdigit():
        return parts[1].replace('_', ' ')
    return t.replace('_', ' ')

def get_global_stats(mb_df):
    """Calculates global stats from MovieBench."""
    if mb_df.empty:
        return {}
    
    return {
        "median": mb_df['duration'].median(),
        "p95": mb_df['duration'].quantile(0.95),
        "std_dev": mb_df['duration'].std(),
        "count": len(mb_df)
    }

def get_reid_frequency(mb_df):
    """
    Insight A: Re-ID Frequency
    Calculates average Cuts Per Minute.
    """
    if mb_df.empty:
        return 0
    
    # Calculate per movie to avoid skewing by total dataset length
    movie_stats = mb_df.groupby('clean_title')['duration'].sum().reset_index()
    movie_stats['minutes'] = movie_stats['duration'] / 60
    movie_stats['shot_count'] = mb_df.groupby('clean_title')['duration'].count().values
    
    # Filter out tiny snippets (trailers/clips < 5 mins)
    valid_movies = movie_stats[movie_stats['minutes'] > 5]
    
    if valid_movies.empty:
        return 0
        
    avg_cpm = (valid_movies['shot_count'] / valid_movies['minutes']).median()
    return avg_cpm

def get_wasteland_stat(mb_df):
    """
    Insight B: The '10-Second Wasteland'
    % of shots between 10s and 30s.
    """
    if mb_df.empty:
        return 0
        
    wasteland_count = mb_df[(mb_df['duration'] >= 10) & (mb_df['duration'] <= 30)].shape[0]
    total_count = len(mb_df)
    
    return (wasteland_count / total_count) * 100

def get_blockbuster_stats(mb_df, hero_df):
    """
    Extracts stats for specific blockbusters from both datasets for the Scatter Plot.
    """
    # 1. Hero Movies
    hero_stats = hero_df.groupby('movie_title')['shot_length_sec'].median().reset_index()
    hero_stats.columns = ['title', 'median_shot']
    
    # 2. Notable MovieBench Movies
    notable_list = [
        "Harry Potter and the order of phoenix", 
        "Harry Potter and the Half-Blood Prince",
        "Indiana Jones and the last crusade",
        "Gran Torino", 
        "Identity Thief", 
        "Vantage Point", 
        "Quantum of Solace", 
        "Spider-Man2",
        "TITANIC",
        "Iron Man",
        "Avatar",
        "Skyfall"
    ]
    
    mb_stats = mb_df[mb_df['clean_title'].isin(notable_list) | mb_df['clean_title'].str.contains("Harry Potter") | mb_df['clean_title'].str.contains("Spider-Man")].groupby('clean_title')['duration'].median().reset_index()
    mb_stats.columns = ['title', 'median_shot']
    
    # Combine
    combined = pd.concat([hero_stats, mb_stats]).drop_duplicates(subset='title')
    return combined.sort_values('median_shot')

def get_bourne_data(hero_df):
    """Returns just the Bourne Ultimatum shots."""
    return hero_df[hero_df['movie_title'] == "The Bourne Ultimatum"].copy()

def get_heatmap_data(mb_df):
    """
    Prepares data for Heatmap of Pace.
    Adds shot_start_time (cumsum) to each movie's shots.
    """
    df = mb_df.copy()
    # Sort to ensure order (MovieBench doesn't strictly guarantee order, but we assume list order is temporal)
    # We don't have shot index in raw CSV, assuming file order is correct per movie grouping
    # Ideally we'd have shot index. Let's group and assume index.
    
    df['shot_idx'] = df.groupby('clean_title').cumcount()
    
    # Calculate start time per movie
    # This is slow if not vectorized.
    # Group by title, then cumsum duration.
    df['end_time'] = df.groupby('clean_title')['duration'].cumsum()
    df['start_time_min'] = (df['end_time'] - df['duration']) / 60.0
    
    return df

def get_genre_data(mb_df):
    """
    Returns a subset of data labeled with genres for the 'Fingerprint' plot.
    """
    # Manual Mapping for high accuracy
    genre_map = {
        'Action': [
            "Harry Potter", "Indiana Jones", "Vantage Point", "Quantum of Solace", 
            "Men in black", "Spider-Man", "Iron Man", "Avatar", "Skyfall", 
            "The Dark Knight", "Inception", "Matrix", "Star Wars", "Fast and Furious",
            "Mission Impossible", "Hunger Games", "Transformers", "X-Men", "Avengers"
        ],
        'Comedy': [
            "This is 40", "Yes man", "Identity Thief", "Horrible Bosses", 
            "The Ugly Truth", "27 Dresses", "Marley and me", "Juno", 
            "Crazy Stupid Love", "Chasing Amy", "Superbad", "Hangover", 
            "Bridesmaids", "Knocked Up", "Step Brothers", "Anchorman"
        ],
        'Drama': [
            "Gran Torino", "Benjamin Button", "Amadeus", "American Beauty", 
            "Forrest Gump", "Gandhi", "Schindler", "Shawshank", "Godfather", 
            "Pulp Fiction", "Fight Club", "Goodfellas", "Social Network", 
            "Moonlight", "Parasite", "Nomadland", "Spotlight", "Birdman", 
            "12 Years a Slave", "Argo", "Kings Speech", "Slumdog Millionaire"
        ]
    }
    
    labeled_dfs = []
    
    for genre, keywords in genre_map.items():
        # Create regex pattern for any keyword
        pattern = '|'.join(keywords)
        mask = mb_df['clean_title'].str.contains(pattern, case=False, regex=True)
        subset = mb_df[mask].copy()
        subset['genre'] = genre
        labeled_dfs.append(subset)
        
    if not labeled_dfs:
        return pd.DataFrame()
        
    return pd.concat(labeled_dfs)

def get_cost_consistency_data(mb_df):
    """
    Calculates the 'Cost of Consistency' curve data.
    X: Duration, Y: % of shots covered.
    """
    # Create a range of durations from 0 to 60s
    durations = np.linspace(0, 60, 120) # 0.5s intervals
    percentages = []
    
    total = len(mb_df)
    if total == 0:
        return pd.DataFrame()
        
    for d in durations:
        count = len(mb_df[mb_df['duration'] <= d])
        percentages.append(count / total * 100)
        
    return pd.DataFrame({'duration': durations, 'percent_covered': percentages})
