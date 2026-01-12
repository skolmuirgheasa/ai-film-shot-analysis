import re
import pandas as pd
import os

# Map log files to movie titles
LOG_FILES = {
    "Mad Max: Fury Road": "snapshot-2026-01-12T23-22-42-580Z.log",
    "The Bourne Ultimatum": "snapshot-2026-01-12T23-23-06-152Z.log",
    "Moulin Rouge!": "snapshot-2026-01-12T23-23-29-178Z.log",
    "Run Lola Run": "snapshot-2026-01-12T23-23-56-610Z.log",
    "Dune (2021)": "snapshot-2026-01-12T23-32-52-382Z.log",
    "John Wick: Chapter 4": "jw4.log",
    "Quantum of Solace": "snapshot-2026-01-12T23-43-21-396Z.log"
}

LOG_DIR_BROWSER = "/Users/griffin/.cursor/browser-logs/"
LOG_DIR_LOCAL = "analysis/logs/"

def parse_log_file(filepath, movie_title):
    shots = []
    print(f"Parsing {movie_title} from {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    re_generic_val = re.compile(r'- generic.*: "?([^"]+)"?')
    captured_values = []
    
    for line in lines:
        line = line.strip()
        match = re_generic_val.search(line)
        if match:
            val = match.group(1)
            # Filter UI text
            if val in ["Close", "Back", "NoS", "LEN", "ASL", "MSL", "MAX", "MIN", "Range", "StDev", "CV", "Show raw data", "Hide colors", "Show colors"]:
                continue
            if "ref=" in val: continue
            captured_values.append(val)
            
    re_int = re.compile(r'^\d+$')
    re_tc = re.compile(r'^\d{2}:\d{2}\.\d$')
    re_float = re.compile(r'^\d+\.?\d*$')
    
    i = 0
    while i < len(captured_values) - 2:
        v1 = captured_values[i]
        v2 = captured_values[i+1]
        v3 = captured_values[i+2]
        
        if re_int.match(v1) and re_tc.match(v2) and re_float.match(v3):
            if int(v1) < 10000:
                shots.append({
                    "movie_title": movie_title,
                    "shot_number": int(v1),
                    "start_time": v2,
                    "shot_length_sec": float(v3)
                })
                i += 3
                continue
        i += 1
    
    print(f"Found {len(shots)} shots for {movie_title}")
    return shots

all_shots = []
for title, filename in LOG_FILES.items():
    path = os.path.join(LOG_DIR_BROWSER, filename)
    if not os.path.exists(path):
        path = os.path.join(LOG_DIR_LOCAL, filename)
        
    if os.path.exists(path):
        all_shots.extend(parse_log_file(path, title))
    else:
        print(f"File not found: {filename}")

df = pd.DataFrame(all_shots)
output_path = "analysis/data/real_shots.csv"
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} total shots to {output_path}")
print(df.groupby('movie_title')['shot_length_sec'].describe())
