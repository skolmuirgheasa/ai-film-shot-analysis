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
    except FileNotFoundError:
        mb_df = pd.DataFrame()
        
    return hero_df, mb_df

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

def get_blockbuster_stats(mb_df, hero_df):
    """
    Extracts stats for specific blockbusters from both datasets for the Scatter Plot.
    Combines Hero movies with notable blockbusters from MovieBench.
    """
    # 1. Hero Movies
    hero_stats = hero_df.groupby('movie_title')['shot_length_sec'].median().reset_index()
    hero_stats.columns = ['title', 'median_shot']
    
    # 2. Notable MovieBench Movies
    # Filter for known blockbusters in MovieBench
    notable_list = [
        "Harry Potter and the order of phoenix", 
        "Harry Potter and the Half-Blood Prince",
        "Indiana Jones and the last crusade",
        "Gran Torino", 
        "Identity Thief", 
        "Vantage Point", 
        "Quantum of Solace", # (MB version)
        "Spider-Man2",
        "TITANIC",
        "The Dark Knight", # If present
        "Inception", # If present
        "Iron Man",
        "Avatar",
        "Skyfall"
    ]
    
    # Clean titles in MB for matching
    def clean_mb_title(t):
        parts = t.split('_', 1)
        if len(parts) > 1 and parts[0].isdigit():
            return parts[1].replace('_', ' ')
        return t.replace('_', ' ')
    
    mb_df['clean_title'] = mb_df['movie_title'].apply(clean_mb_title)
    
    mb_stats = mb_df[mb_df['clean_title'].isin(notable_list) | mb_df['clean_title'].str.contains("Harry Potter") | mb_df['clean_title'].str.contains("Spider-Man")].groupby('clean_title')['duration'].median().reset_index()
    mb_stats.columns = ['title', 'median_shot']
    
    # Combine
    combined = pd.concat([hero_stats, mb_stats]).drop_duplicates(subset='title')
    return combined.sort_values('median_shot')

def get_bourne_data(hero_df):
    """Returns just the Bourne Ultimatum shots."""
    return hero_df[hero_df['movie_title'] == "The Bourne Ultimatum"].copy()

