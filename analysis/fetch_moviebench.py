import os
import pandas as pd
from datasets import load_dataset
import time

def fetch_moviebench_data():
    print("Initializing MovieBench download (Streaming Mode)...")
    output_path = "analysis/data/moviebench_shots.csv"
    
    try:
        # Use streaming=True to avoid local caching/casting errors
        # This allows us to process the dataset on the fly
        dataset = load_dataset("weijiawu/MovieBench", split="train", streaming=True)
        
        print("Dataset stream initialized. Iterating...")
        
        all_shots = []
        movie_count = 0
        
        # Iterate through the stream
        for i, entry in enumerate(dataset):
            movie_title = entry.get('movie_name', f'Unknown_{i}')
            
            # The structure for shots in MovieBench needs to be checked.
            # Based on the user's snippet, it's entry['shots']
            shots = entry.get('shots', [])
            
            # If shots is None or empty, skip
            if not shots:
                continue
                
            movie_has_shots = False
            for shot in shots:
                duration = shot.get('duration', 0)
                
                # Fallback: calculate from start/end if duration is missing
                if duration == 0:
                    start = shot.get('start', 0)
                    end = shot.get('end', 0)
                    if end > start:
                        duration = end - start
                        
                if duration > 0:
                    all_shots.append({
                        "movie_title": movie_title,
                        "duration": float(duration)
                    })
                    movie_has_shots = True
            
            if movie_has_shots:
                movie_count += 1
                
            # Log progress
            if i % 10 == 0:
                print(f"Processed {i} movies... Found {len(all_shots)} shots so far.")
            
            # Safety break for testing (remove for full run, but let's get a good sample first)
            # The dataset might be huge. Let's aim for ~50 movies or ~5000 shots to prove the point quickly.
            # User wants "Big Data", so let's try to get a decent amount.
            if len(all_shots) > 20000: 
                print("Reached 20,000 shots. Stopping stream.")
                break
        
        if not all_shots:
            print("No shots extracted. Debugging first entry keys:")
            first = next(iter(dataset))
            print(first.keys())
            return

        df = pd.DataFrame(all_shots)
        print(f"Extraction Complete. {len(df)} shots from {movie_count} movies.")
        print(f"Median Shot Length: {df['duration'].median():.2f}s")
        print(f"Max Shot Length: {df['duration'].max():.2f}s")
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
        
    except Exception as e:
        print(f"Error fetching MovieBench: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fetch_moviebench_data()
