import pandas as pd
import re

def inspect_moviebench():
    print("Loading MovieBench data...")
    try:
        df = pd.read_csv("analysis/data/moviebench_shots.csv")
    except FileNotFoundError:
        print("Data not found. Run previous steps first.")
        return

    print(f"Total Shots: {len(df)}")
    print(f"Total Movies: {df['movie_title'].nunique()}")
    
    # 1. Identify Notable/Recent Movies
    # MovieBench titles often look like "1037_The_Curious_Case_Of_Benjamin_Button"
    # We can clean them up for better readability.
    
    def clean_title(t):
        # Remove leading digits and underscores
        # pattern: digits_Name_Of_Movie
        parts = t.split('_', 1)
        if len(parts) > 1 and parts[0].isdigit():
            return parts[1].replace('_', ' ')
        return t.replace('_', ' ')

    df['clean_title'] = df['movie_title'].apply(clean_title)
    
    unique_movies = df['clean_title'].unique()
    print("\n--- Sample of Notable Movies in Dataset ---")
    # Let's pick some known titles if present
    notable_keywords = ["Harry Potter", "Spider-Man", "Iron Man", "Batman", "Avengers", "Inception", "Titanic", "Avatar", "Star Wars", "Matrix", "Bond", "Mission Impossible", "Fast and Furious", "Hunger Games", "Twilight", "Lord of the Rings", "Hobbit", "Pirates", "Transformers", "X-Men", "Shrek", "Toy Story", "Frozen", "Lion King", "Finding Nemo", "Despicable Me", "Ice Age", "Madagascar", "Kung Fu Panda", "Cars", "Up", "Wall-E", "Ratatouille", "Incredibles", "Monsters Inc", "Nemo", "Dory", "Zootopia", "Inside Out", "Coco", "Moana", "Sing", "Pets", "Minions", "Lego", "Grinch", "Elf", "Home Alone", "Night at the Museum", "Jumanji", "Men in Black", "Ghostbusters", "Back to the Future", "Indiana Jones", "Jurassic Park", "Jaws", "E.T.", "Forrest Gump", "Godfather", "Pulp Fiction", "Fight Club", "Matrix", "Goodfellas", "Shawshank", "Schindler", "Private Ryan", "Green Mile", "Gladiator", "Beautiful Mind", "Departed", "No Country", "Slumdog", "Hurt Locker", "King's Speech", "Artist", "Argo", "12 Years", "Birdman", "Spotlight", "Moonlight", "Shape of Water", "Green Book", "Parasite", "Nomadland", "CODA", "Everything", "Crash", "Million Dollar Baby", "Chicago", "Rings", "Shakespeare", "Titanic", "English Patient", "Braveheart", "Gump", "List", "Silence", "Unforgiven", "Dances", "Driving", "Rain Man", "Emperor", "Platoon", "Africa", "Amadeus", "Terms", "Gandhi", "Chariots", "People", "Kramer", "Hunter", "Annie Hall", "Rocky", "Cuckoo", "Godfather", "Connection", "Patton", "Cowboy", "Oliver", "Heat", "Man for All Seasons", "Sound of Music", "Lady", "Jones", "Lawrence", "West Side", "Apartment", "Ben-Hur", "Gigi", "Kwai", "World", "Marty", "Waterfront", "Here to Eternity", "Show", "American", "All About Eve", "Men", "Hamlet", "Gentleman", "Best Years", "Lost Weekend", "Way", "Casablanca", "Mrs. Miniver", "Valley", "Rebecca", "Wind", "take it with you", "Emile", "Zola", "Great Ziegfeld", "Mutiny", "Night", "Cavalcade", "Grand Hotel", "Cimarron", "All Quiet", "Broadway", "Wings"]
    
    found_notables = []
    for title in unique_movies:
        for key in notable_keywords:
            if key.lower() in title.lower():
                found_notables.append(title)
                break
    
    # Sort and print a unique list
    for title in sorted(list(set(found_notables)))[:20]: # Print first 20 found
        print(f"- {title}")
    print(f"(...and {len(unique_movies) - 20} more)")

    # 2. Find Movies with NO shot > 20s
    print("\n--- Movies with Max Shot < 20 Seconds ---")
    
    movie_stats = df.groupby('clean_title')['duration'].agg(['max', 'count', 'median']).reset_index()
    
    # Filter: Max shot < 20s AND reasonable shot count (e.g. > 100 shots to be a real sample)
    strict_ceiling_movies = movie_stats[ (movie_stats['max'] < 20.0) & (movie_stats['count'] > 50) ].sort_values('max')
    
    if not strict_ceiling_movies.empty:
        print(f"Found {len(strict_ceiling_movies)} movies adhering to strict 20s ceiling:")
        print(strict_ceiling_movies[['clean_title', 'max', 'median', 'count']].to_string(index=False))
    else:
        print("No movies found with STRICT max < 20s in this dataset.")
        
    # Let's also look for "Soft Ceiling" (e.g. 99% < 20s)
    print("\n--- Movies with 'Soft Ceiling' (99% shots < 20s) ---")
    
    # Helper to calc percentile
    def pct_under_20(series):
        return (series < 20).mean() * 100
        
    df_grouped = df.groupby('clean_title')['duration'].apply(pct_under_20).reset_index(name='pct_under_20')
    soft_ceiling = df_grouped[df_grouped['pct_under_20'] >= 99.0].sort_values('pct_under_20', ascending=False)
    
    # Join with metadata for context
    soft_ceiling = soft_ceiling.merge(movie_stats, on='clean_title')
    # Filter for decent sample size
    soft_ceiling = soft_ceiling[soft_ceiling['count'] > 100]
    
    print(f"Found {len(soft_ceiling)} movies where >99% of shots are under 20s:")
    print(soft_ceiling[['clean_title', 'pct_under_20', 'max', 'count']].head(15).to_string(index=False))

if __name__ == "__main__":
    inspect_moviebench()

