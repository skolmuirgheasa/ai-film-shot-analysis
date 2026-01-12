import requests
import re
import pandas as pd
import os

MOVIES = [
    {"title": "Dune (2021)", "id": "dc0e0457-4ce8-458f-9225-3ccc8fd7938b"},
    {"title": "John Wick: Chapter 4", "id": "b056ddd6-0895-4595-a440-90d8646bd8a4"},
    # Add more here
]

def get_cinemetrics_data(movie_id, movie_title):
    url = f"https://cinemetrics.uchicago.edu/movie/{movie_id}"
    print(f"Scraping {movie_title} from {url}...")
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to load page: {response.status_code}")
            return None

        # Regex to find the hidden data array in the HTML source
        # User suggested: shot_lengths = [24, 12, 55, ...];
        # Let's try flexible regex
        match = re.search(r'shot_lengths\s*=\s*\[(.*?)\]', response.text)
        
        # Also try looking for other patterns if that fails, purely based on observation of what variable names might be
        if not match:
            # Maybe it's buried in a Next.js prop or something?
            # Let's check for the raw data pattern we saw in the logs if this fails.
            pass

        if match:
            # Convert string list "10, 20, 30" to float list
            # Cinemetrics data is often in 1/10th of a second. e.g. "24" = 2.4s
            raw_data = [float(x.strip()) / 10.0 for x in match.group(1).split(',') if x.strip()]
            
            df = pd.DataFrame(raw_data, columns=['duration'])
            df['movie_title'] = movie_title
            
            # basic stats
            print(f"Found {len(df)} shots.")
            print(f"Total Runtime: {df['duration'].sum() / 60:.2f} minutes")
            print(f"Median Shot: {df['duration'].median()}s")
            print(f"Max Shot: {df['duration'].max()}s")
            
            return df
        else:
            print("Could not find shot_lengths in page source. Dumping snippet...")
            # print(response.text[:1000])
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
        output_path = "analysis/data/scraped_shots.csv"
        final_df.to_csv(output_path, index=False)
        print(f"Saved {len(final_df)} shots to {output_path}")

