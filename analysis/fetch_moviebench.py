import os
import pandas as pd
from datasets import load_dataset

def fetch_moviebench_data():
    print("Initializing MovieBench download...")
    
    # Check if we have cached data first
    output_path = "analysis/data/moviebench_shots.csv"
    
    # We want 'shot_level' annotations.
    # The dataset structure is: 'weijiawu/MovieBench'
    # It likely has subsets. Let's try loading the default or inspecting.
    
    try:
        # Load the dataset
        # The user mentioned "shot_level annotations".
        # Let's load the train split.
        print("Downloading dataset from Hugging Face (this may take a while)...")
        dataset = load_dataset("weijiawu/MovieBench", split="train")
        
        print(f"Dataset loaded. Features: {dataset.features}")
        
        all_shots = []
        
        # Iterate and extract
        for entry in dataset:
            # Structure check: 'movie_name', 'shots' (list of dicts?)
            movie_title = entry.get('movie_name', 'Unknown')
            
            # The shots might be under 'shots' or 'scene_structure' etc.
            # Based on user snippet: entry['shots']
            
            shots = entry.get('shots', [])
            if not shots:
                # Try finding other keys if 'shots' is missing
                continue
                
            for shot in shots:
                duration = shot.get('duration', 0)
                # Some datasets use start/end times
                if duration == 0:
                    start = shot.get('start', 0)
                    end = shot.get('end', 0)
                    if end > start:
                        duration = end - start
                        
                if duration > 0:
                    all_shots.append({
                        "movie_title": movie_title,
                        "duration": duration
                    })
        
        if not all_shots:
            print("No shots found in dataset structure. Debugging keys...")
            print(dataset[0].keys())
            return

        df = pd.DataFrame(all_shots)
        print(f"Extracted {len(df)} shots from {len(df['movie_title'].unique())} movies.")
        print(f"Median Shot Length: {df['duration'].median():.2f}s")
        
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
        
    except Exception as e:
        print(f"Error fetching MovieBench: {e}")
        # Fallback if structure is different
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fetch_moviebench_data()

