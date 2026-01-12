import re
import pandas as pd
import os
import glob

# Map log files to movie titles
LOG_FILES = {
    "Mad Max: Fury Road": "snapshot-2026-01-12T23-22-42-580Z.log",
    "The Bourne Ultimatum": "snapshot-2026-01-12T23-23-06-152Z.log",
    "Moulin Rouge!": "snapshot-2026-01-12T23-23-29-178Z.log",
    "Run Lola Run": "snapshot-2026-01-12T23-23-56-610Z.log"
}

LOG_DIR = "/Users/griffin/.cursor/browser-logs/"

def parse_log_file(filepath, movie_title):
    shots = []
    print(f"Parsing {movie_title} from {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()

    # The pattern seems to be groups of 3 generics with values: "Shot #", "Time", "Duration"
    # Example:
    # - generic [ref=e3228]:
    #   - generic [ref=e3229]: "2"
    #   - generic [ref=e3230]: 00:15.7
    #   - generic [ref=e3231]: "19.4"
    
    # We can regex for lines that look like values.
    # Pattern:  - generic.*: "(\d+)"  (Shot Num)
    #           - generic.*: ([\d:.]+) (Time)
    #           - generic.*: "([\d.]+)" (Duration)
    
    # Since the lines are sequential, we can iterate line by line and state machine it.
    
    lines = content.split('\n')
    current_shot = {}
    
    # Regex for values
    # Matches: - generic [ref=e3225]: "1"
    re_shot_num = re.compile(r'- generic.*: "(\d+)"')
    # Matches: - generic [ref=e3226]: 00:00.0   OR  - generic [ref=...]: "00:00.0"
    re_time = re.compile(r'- generic.*: "?(\d{2}:\d{2}\.\d)"?')
    # Matches: - generic [ref=e3227]: "15.7"
    re_duration = re.compile(r'- generic.*: "(\d+\.?\d*)"')
    
    # A looser regex for just values in generic blocks
    re_generic_val = re.compile(r'- generic.*: "?([^"]+)"?')

    # Let's try to capture blocks of 3 values
    # The structure is nested under a parent generic, but indentation might vary.
    # Let's collect all "generic" values and see if they form triplets.
    
    # Actually, looking at the grep output:
    #       - generic [ref=e3224]:
    #         - generic [ref=e3225]: "1"
    #         - generic [ref=e3226]: 00:00.0
    #         - generic [ref=e3227]: "15.7"
    
    # So we are looking for a sequence of 3 lines defining values.
    
    captured_values = []
    
    for line in lines:
        line = line.strip()
        # Check if line has a value
        match = re_generic_val.search(line)
        if match:
            val = match.group(1)
            # Filter out UI text like "Close", "Back", "NoS", etc.
            if val in ["Close", "Back", "NoS", "LEN", "ASL", "MSL", "MAX", "MIN", "Range", "StDev", "CV", "Show raw data", "Hide colors", "Show colors"]:
                continue
            if "ref=" in val: # It's a key, not value
                continue
            
            captured_values.append(val)
            
    # Now scan the captured values for patterns of (Int, Timecode, Float)
    # Shot Num is int, Timecode is MM:SS.d, Duration is Float
    
    re_int = re.compile(r'^\d+$')
    re_tc = re.compile(r'^\d{2}:\d{2}\.\d$')
    re_float = re.compile(r'^\d+\.?\d*$')
    
    i = 0
    while i < len(captured_values) - 2:
        v1 = captured_values[i]
        v2 = captured_values[i+1]
        v3 = captured_values[i+2]
        
        if re_int.match(v1) and re_tc.match(v2) and re_float.match(v3):
            # Verify consistency (shot numbers should increment, but let's just trust for now)
            # Also check if v1 is likely a shot number (e.g. < 5000)
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
    path = os.path.join(LOG_DIR, filename)
    if os.path.exists(path):
        all_shots.extend(parse_log_file(path, title))
    else:
        print(f"File not found: {path}")

df = pd.DataFrame(all_shots)
output_path = "analysis/data/real_shots.csv"
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} total shots to {output_path}")

# Quick verify
print(df.groupby('movie_title')['shot_length_sec'].describe())

