from huggingface_hub import hf_hub_download
import json
import pandas as pd
import os

def inspect_and_parse():
    print("Loading cached movies_scenes.json...")
    # We know the path from the previous run output, or just redownload (it's cached)
    file_path = hf_hub_download(repo_id="weijiawu/MovieBench", filename="movies_scenes.json", repo_type="dataset")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    # Get first value
    first_key = list(data.keys())[0]
    first_entry = data[first_key]
    
    print(f"Structure for {first_key}:")
    print(first_entry.keys())
    
    # Check if 'shots' is a key, or if it's a list of scenes?
    # Usually "movies_scenes" implies scenes.
    # Let's see if scenes have shots.
    
    if 'scene' in first_entry:
        print("Found 'scene' key. Inspecting first scene...")
        scenes = first_entry['scene']
        if len(scenes) > 0:
            print(scenes[0].keys())
            # check for shots inside scene
            if 'shots' in scenes[0]:
                print("Found 'shots' in scene!")
                print(scenes[0]['shots'][0])
    
    # Try to parse based on inspection
    all_shots = []
    
    for movie_id, content in data.items():
        # MovieBench structure seems to be: { "movie_id": { "scene": [ { "scene_id":..., "shots": [...] } ] } }
        # Or maybe "shots" are top level?
        
        # Let's look for shots anywhere
        
        scenes = content.get('scene', [])
        for scene in scenes:
            shots = scene.get('shots', [])
            for shot in shots:
                # Shot structure?
                # Usually has 'shot_id', 'shot_start', 'shot_end' or 'duration'
                
                # Check for start/end in frames or seconds?
                # If frames, we need FPS.
                
                start = shot.get('shot_start_frame', 0)
                end = shot.get('shot_end_frame', 0)
                fps = 24.0 # Default assumption if not found, but we should look for metadata
                
                # Try to find duration directly
                # If not, try to find timecodes
                
                if 'shot_duration' in shot:
                    duration = float(shot['shot_duration'])
                    all_shots.append({"movie": movie_id, "duration": duration})
                elif end > start:
                    # frames?
                    duration = (end - start) / fps
                    all_shots.append({"movie": movie_id, "duration": duration})
                    
    print(f"Extracted {len(all_shots)} shots.")
    if len(all_shots) > 0:
        df = pd.DataFrame(all_shots)
        print(df.describe())
        df.to_csv("analysis/data/moviebench_shots.csv", index=False)

if __name__ == "__main__":
    inspect_and_parse()

