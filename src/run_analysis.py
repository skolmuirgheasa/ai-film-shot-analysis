import stats
import visualization
import pandas as pd
import os

def main():
    print("Starting Analysis Pipeline...")
    
    # 1. Load Data
    hero_df, mb_df = stats.load_data()
    
    if hero_df.empty or mb_df.empty:
        print("Error: Missing data files in data/. Run fetch/parse scripts first.")
        return

    # 2. Generate Stats for README
    global_stats = stats.get_global_stats(mb_df)
    print("\n--- GLOBAL STATS (MovieBench) ---")
    print(global_stats)
    
    # 3. Generate Blockbuster Specifics
    blockbuster_data = stats.get_blockbuster_stats(mb_df, hero_df)
    
    # 4. Generate Visuals
    print("\nGenerating Visuals...")
    os.makedirs("plots", exist_ok=True)
    
    # Visual 1: Barcode (Bourne)
    bourne_data = stats.get_bourne_data(hero_df)
    if not bourne_data.empty:
        visualization.plot_barcode_timeline(bourne_data)
    else:
        print("Warning: Bourne Ultimatum data not found for barcode plot.")
        
    # Visual 2: CDF (MovieBench)
    visualization.plot_cumulative_density(mb_df)
    
    # Visual 3: Scatter (Blockbusters)
    visualization.plot_ceiling_scatter(blockbuster_data)
    
    print("\nAnalysis Complete. Check plots/ and README.md.")

if __name__ == "__main__":
    main()

