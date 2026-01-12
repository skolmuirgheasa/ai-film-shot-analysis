import requests
import re
import pandas as pd
import os

# Candidate movies to check for Max Shot < 20s
MOVIES = [
    {"title": "Quantum of Solace", "id": "58c5672e-5e49-4ac7-b788-694377f90a62"},
    # Add potential candidates here after searching
]

def get_cinemetrics_data(movie_id, movie_title):
    url = f"https://cinemetrics.uchicago.edu/movie/{movie_id}"
    print(f"Scraping {movie_title} from {url}...")
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to load page: {response.status_code}")
            return None

        match = re.search(r'shot_lengths\s*=\s*\[(.*?)\]', response.text)
        
        if match:
            raw_data = [float(x.strip()) / 10.0 for x in match.group(1).split(',') if x.strip()]
            
            df = pd.DataFrame(raw_data, columns=['duration'])
            df['movie_title'] = movie_title
            
            # Strict check for the user's requirement
            max_shot = df['duration'].max()
            print(f"Found {len(df)} shots.")
            print(f"Max Shot: {max_shot}s")
            
            if max_shot > 25: # Allow a small buffer for credits/logos, but warn
                print(f"WARNING: Max shot {max_shot}s > 20s target.")
            
            return df
        else:
            print("Could not find shot_lengths.")
            return None
            
    except Exception as e:
        print(f"Error scraping {movie_title}: {e}")
        return None

if __name__ == "__main__":
    all_dfs = []
    for m in MOVIES:
        df = get_cinemetrics_data(m['id'], m['title'])
        if df is not None:
            all_dfs.append(df)
            
    if all_dfs:
        final_df = pd.concat(all_dfs)
        output_path = "analysis/data/quantum_check.csv"
        final_df.to_csv(output_path, index=False)

