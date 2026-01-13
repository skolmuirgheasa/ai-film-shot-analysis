import json
import pandas as pd
import os
from huggingface_hub import hf_hub_download
import re

def parse_timestamp(ts_str):
    # Format: HH.MM.SS.mmm
    try:
        parts = ts_str.split('.')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        milliseconds = int(parts[3])
        
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    except:
        return 0

def parse_mb_structure():
    print("Loading cached movies_scenes.json...")
    file_path = hf_hub_download(repo_id="weijiawu/MovieBench", filename="movies_scenes.json", repo_type="dataset")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    all_shots = []
    
    # Regex to capture timestamps at the end of the string
    # Pattern: _(HH.MM.SS.mmm)-(HH.MM.SS.mmm)$
    re_ts = re.compile(r'_(\d{2}\.\d{2}\.\d{2}\.\d{3})-(\d{2}\.\d{2}\.\d{2}\.\d{3})$')
    
    for movie_id, scenes_dict in data.items():
        for scene_desc, shot_list in scenes_dict.items():
            if not isinstance(shot_list, list):
                continue
                
            for shot_str in shot_list:
                if not isinstance(shot_str, str):
                    continue
                    
                match = re_ts.search(shot_str)
                if match:
                    start_str = match.group(1)
                    end_str = match.group(2)
                    
                    start_sec = parse_timestamp(start_str)
                    end_sec = parse_timestamp(end_str)
                    
                    if end_sec > start_sec:
                        duration = end_sec - start_sec
                        all_shots.append({
                            "movie_title": movie_id, # Using ID as title for now
                            "duration": duration
                        })

    print(f"Extracted {len(all_shots)} shots.")
    
    if len(all_shots) > 0:
        df = pd.DataFrame(all_shots)
        print(f"Median Shot Length: {df['duration'].median():.2f}s")
        print(f"Max Shot Length: {df['duration'].max():.2f}s")
        
        output_path = "analysis/data/moviebench_shots.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

if __name__ == "__main__":
    parse_mb_structure()
