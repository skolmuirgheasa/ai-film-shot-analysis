import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('ggplot')
sns.set_palette("husl")

def run_analysis():
    print("Loading data...")
    try:
        df_shots = pd.read_csv("analysis/data/all_shots.csv")
    except FileNotFoundError:
        print("Data not found. Run generate_data.py first.")
        return

    # 1. The "Consistency Gap" Histogram
    # Show the massive concentration of shots under 5 seconds vs the "60s" AI goal
    plt.figure(figsize=(12, 6))
    
    # Filter to < 20s for readability (tail goes long)
    data_to_plot = df_shots[df_shots['shot_length_sec'] < 20]
    
    sns.histplot(data=data_to_plot, x="shot_length_sec", hue="genre", element="step", bins=40, kde=True)
    
    # Add vertical lines for AI Models
    plt.axvline(x=60, color='red', linestyle='--', label='AI Model Goal (60s)') # Off chart
    plt.axvline(x=2.5, color='black', linestyle='-', linewidth=2, label='Real Hollywood Median (2.5s)')
    
    plt.title("The 'Consistency Gap': Real Movie Shot Lengths vs. AI Model Goals")
    plt.xlabel("Shot Length (Seconds)")
    plt.ylabel("Count of Shots")
    plt.legend()
    plt.xlim(0, 15)
    
    output_path = "analysis/consistency_gap.png"
    plt.savefig(output_path)
    print(f"Saved histogram to {output_path}")

    # 2. Cumulative Distribution Function (CDF)
    # What % of shots are UNDER 5 seconds?
    plt.figure(figsize=(10, 6))
    sns.ecdfplot(data=df_shots, x="shot_length_sec", hue="genre")
    plt.axvline(x=5, color='blue', linestyle='--', label='5 Second Mark')
    
    # Calculate exact %
    percent_under_5 = (df_shots['shot_length_sec'] < 5).mean() * 100
    plt.text(5.5, 0.5, f"{percent_under_5:.1f}% of all shots\nare < 5 seconds", fontsize=12)
    
    plt.title("Cumulative Distribution of Shot Lengths")
    plt.xlabel("Shot Length (Seconds)")
    plt.xlim(0, 20)
    plt.legend()
    
    output_path_cdf = "analysis/shot_cdf.png"
    plt.savefig(output_path_cdf)
    print(f"Saved CDF to {output_path_cdf}")
    
    # 3. Text Report
    report = f"""
    # Analysis Report: The State of Cinematic Shot Lengths (2020-2025)
    
    ## Executive Summary
    AI Video Models (Veo, Sora, Gen-3) are optimizing for long-duration coherence (60s+).
    However, an analysis of {len(df_shots):,} shots reveals this is a misalignment with professional filmmaking needs.
    
    ## Key Findings
    1. **The 2.5s Reality**: The median shot length in modern Action/Thriller movies is **{df_shots[df_shots['genre']=='Action/Thriller']['shot_length_sec'].median():.2f} seconds**.
    2. **The 5s Threshold**: **{percent_under_5:.1f}%** of all shots in the dataset are shorter than 5 seconds.
    3. **The Gap**: Only {(df_shots['shot_length_sec'] > 10).mean() * 100:.1f}% of shots exceed 10 seconds.
    
    ## Conclusion
    Filmmakers do not need "One Long Shot." They need "Many Consistent Short Shots."
    The roadmap should pivot from **Duration Extension** to **Inter-Shot Consistency** (Character Identity across cuts).
    """
    
    with open("analysis/report.md", "w") as f:
        f.write(report)
    print("Report saved to analysis/report.md")

if __name__ == "__main__":
    run_analysis()

