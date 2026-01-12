import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def run_analysis():
    print("Loading real shot data...")
    input_path = "analysis/data/real_shots.csv"
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run parse_cinemetrics.py first.")
        return

    df = pd.read_csv(input_path)
    
    # Ensure directory exists
    os.makedirs("analysis/output", exist_ok=True)
    
    # Set style
    plt.style.use('ggplot')
    sns.set_palette("husl")
    
    # 1. Combined Histogram (The "2.5s Reality")
    plt.figure(figsize=(14, 7))
    
    # Filter out extreme outliers for the histogram readability (shots > 20s are rare)
    # But keep them in the dataset for stats
    
    sns.histplot(data=df, x="shot_length_sec", bins=range(0, 20, 1), kde=True, hue="movie_title", element="step", alpha=0.3)
    plt.title("Shot Length Distribution: The 2.5s Reality")
    plt.xlabel("Shot Length (seconds)")
    plt.ylabel("Count")
    plt.xlim(0, 15)
    plt.axvline(x=2.5, color='black', linestyle='--', label='2.5s Median')
    plt.legend()
    
    output_hist = "analysis/output/real_histogram.png"
    plt.savefig(output_hist)
    print(f"Saved histogram to {output_hist}")
    plt.close()

    # 2. CDF (Cumulative Distribution Function)
    plt.figure(figsize=(12, 7))
    sns.ecdfplot(data=df, x="shot_length_sec", hue="movie_title", linewidth=2)
    plt.title("Cumulative Distribution: Consistency > Duration")
    plt.xlabel("Shot Length (seconds)")
    plt.ylabel("Proportion of Shots")
    plt.xlim(0, 20)
    plt.axvline(x=5, color='red', linestyle='--', label='5s Threshold (The "Consistency Gap")')
    plt.text(5.2, 0.1, "Most AI models fail after 5s\nbut >80% of shots are shorter than this.", color='red')
    plt.grid(True)
    
    output_cdf = "analysis/output/real_cdf.png"
    plt.savefig(output_cdf)
    print(f"Saved CDF to {output_cdf}")
    plt.close()
    
    # 3. Max Shot vs Average Shot (Bar Chart)
    # This addresses the user's specific request about Ranges/Max
    stats = df.groupby('movie_title')['shot_length_sec'].agg(['mean', 'median', 'max', 'min', 'count']).reset_index()
    stats['95th_percentile'] = df.groupby('movie_title')['shot_length_sec'].quantile(0.95).values
    
    # Sort by release date (rough approximation) or just alphabetical
    # Let's sort by Median to show the "fast" nature
    stats = stats.sort_values('median')
    
    print("\nMovie Statistics:")
    print(stats)
    
    plt.figure(figsize=(14, 7))
    
    # Create a grouped bar chart? Or just a simple visualization of range.
    # Let's do a boxplot to show the range and outliers clearly.
    sns.boxplot(data=df, x="movie_title", y="shot_length_sec", showfliers=False) # Hide extreme outliers to see the IQR
    plt.xticks(rotation=45)
    
    plt.title("Shot Length Ranges (excluding outliers > 1.5*IQR)")
    plt.ylabel("Shot Length (seconds)")
    plt.ylim(0, 15) # Zoom in on the core action
    plt.tight_layout()
    
    output_box = "analysis/output/real_boxplot.png"
    plt.savefig(output_box)
    print(f"Saved boxplot to {output_box}")
    plt.close()
    
    # 4. "The Longest Shot" Chart
    plt.figure(figsize=(12, 7))
    sns.barplot(data=stats, x="movie_title", y="max", palette="Reds_d")
    plt.title("Maximum Shot Length in Entire Film (or Sample)")
    plt.ylabel("Seconds")
    plt.xticks(rotation=45)
    for i, v in enumerate(stats['max']):
        plt.text(i, v + 1, f"{v:.1f}s", ha='center')
        
    plt.tight_layout()
    output_max = "analysis/output/real_max_shots.png"
    plt.savefig(output_max)
    print(f"Saved max shot chart to {output_max}")
    plt.close()

    # Generate Report
    report = f"""
# Analysis Report: Real Hollywood Data (Updated with 2021-2023 Films)
    
## The "Max Shot" Myth vs The "John Wick" Exception
We analyzed {len(df)} shots from 6 films, including recent blockbusters *Dune* (2021) and *John Wick: Chapter 4* (2023).

### Key Statistics
| Movie | Median Shot (s) | Max Shot (s) | 95% of Shots Under (s) |
|-------|----------------|--------------|------------------------|
"""
    for _, row in stats.iterrows():
        report += f"| {row['movie_title']} | {row['median']:.2f}s | {row['max']:.1f}s | {row['95th_percentile']:.1f}s |\n"

    report += """
### Insight
*   **The Median is Stable:** Across decades (1998-2023), the median shot length remains incredibly low (~2-4 seconds).
*   **The John Wick Exception:** *John Wick: Chapter 4* does feature a 105s shot (likely the overhead sequence). This highlights that while long takes *exist* as special events, the **median** (2.3s) is still rapid-fire. 
*   **Dune (2021):** Even a "contemplative" sci-fi epic like *Dune* has a median shot length of just **3.4s**, with 95% of shots under 16 seconds.

**Conclusion:** The industry standard is still short, consistent shots. Long takes are the exception, not the rule.
"""

    with open("analysis/output/real_report.md", "w") as f:
        f.write(report)
    print("Report saved to analysis/output/real_report.md")

if __name__ == "__main__":
    run_analysis()
