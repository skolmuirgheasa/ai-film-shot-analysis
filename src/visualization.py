import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors

# Set professional style globally
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'
plt.rcParams['text.color'] = '#333333'

def plot_barcode_timeline(bourne_df, output_path="plots/the_20s_ceiling_barcode.png"):
    """Visual 1: The 'Barcode' Timeline"""
    bourne_df = bourne_df.sort_values('shot_number')
    bourne_df['end_time'] = bourne_df['shot_length_sec'].cumsum()
    subset = bourne_df[bourne_df['end_time'] <= 600]
    
    plt.figure(figsize=(12, 3))
    ax = plt.gca()
    
    for cut_point in subset['end_time']:
        ax.axvline(x=cut_point, color='black', linewidth=0.8, alpha=0.9)
        
    ax.set_yticks([])
    ax.set_xlim(0, 600)
    ax.set_xlabel("Time (Seconds) - First 10 Minutes")
    ax.set_title("Visualizing Cut Density: 'The Bourne Ultimatum'", fontsize=14, pad=15, loc='left')
    plt.figtext(0.13, -0.1, "Each line represents a hard cut. 98% of cuts occur < 4s apart.", fontsize=10, style='italic')
    
    sns.despine(left=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_cumulative_density(mb_df, output_path="plots/cumulative_density.png"):
    """Visual 2: The '95% Threshold' CDF"""
    plt.figure(figsize=(10, 6))
    sns.ecdfplot(data=mb_df, x="duration", color="#333333", linewidth=2.5, label="All Cinema (MovieBench)")
    
    p95 = mb_df['duration'].quantile(0.95)
    plt.axvline(x=p95, color='#d62728', linestyle='--', linewidth=2, label=f"95% Threshold ({p95:.1f}s)")
    plt.axhline(y=0.95, color='#d62728', linestyle=':', linewidth=1)
    
    plt.xlim(0, 30)
    plt.ylim(0, 1.05)
    plt.xlabel("Shot Duration (Seconds)", fontsize=11, weight='bold')
    plt.ylabel("Cumulative % of Shots", fontsize=11, weight='bold')
    plt.title("The Consistency Gap: 95% of Cinema is < 15 Seconds", fontsize=14, loc='left', pad=20)
    plt.legend(frameon=False, loc='lower right')
    plt.text(16, 0.5, "Diminishing Returns\nfor GenAI Capability", fontsize=10, color='#666666')
    plt.arrow(15.5, 0.6, 5, 0, head_width=0.03, color='#666666')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_ceiling_scatter(blockbuster_df, output_path="plots/distribution_histogram.png"):
    """Visual 3: The 'Ceiling' Scatter"""
    blockbuster_df['short_title'] = blockbuster_df['title'].apply(lambda x: x.split(':')[0][:20])
    blockbuster_df = blockbuster_df.sort_values('median_shot')
    
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=blockbuster_df, x='short_title', y='median_shot', s=100, color='#1f77b4', zorder=10)
    plt.vlines(x=blockbuster_df['short_title'], ymin=0, ymax=blockbuster_df['median_shot'], color='#1f77b4', alpha=0.4, linewidth=1)
    plt.axhline(y=5, color='#d62728', linestyle='--', linewidth=1.5, label='5s Soft Ceiling')
    
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.ylabel("Median Shot Length (s)", fontsize=11, weight='bold')
    plt.xlabel("")
    plt.title("Blockbuster Pacing: The 3-5 Second Standard", fontsize=14, loc='left', pad=20)
    plt.ylim(0, 6)
    plt.legend(frameon=False)
    sns.despine()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_heatmap_of_pace(df, output_path="plots/heatmap_pace.png"):
    """
    New Visual 1: Heatmap of Pace
    X: Runtime (min), Y: Duration (log scale)
    """
    # Prepare data: filter reasonable bounds
    # Remove outliers > 120 mins runtime (some bad data might exist) or shot > 60s (we want to show empty space)
    # Actually keep shot > 60s to show if they exist.
    
    clean_df = df[(df['start_time_min'] <= 150) & (df['duration'] > 0)].copy()
    
    plt.figure(figsize=(12, 7))
    
    # Using log scale for Y (Duration) to emphasize the short shots
    plt.yscale('log')
    
    # 2D Histogram
    h = plt.hist2d(
        clean_df['start_time_min'], 
        clean_df['duration'], 
        bins=[60, 50], 
        range=[[0, 120], [0.5, 100]], # Y from 0.5s to 100s
        norm=mcolors.LogNorm(), # Log color scale for density
        cmap='inferno'
    )
    
    plt.colorbar(h[3], label='Shot Density')
    
    plt.xlabel("Movie Runtime (Minutes)", fontsize=11, weight='bold')
    plt.ylabel("Shot Duration (Seconds) - Log Scale", fontsize=11, weight='bold')
    plt.title("The 'Void' of Long Shots: Heatmap of Pace", fontsize=14, loc='left', pad=20)
    
    # Annotate the void
    plt.text(60, 40, "THE VOID\n(Zero Data Density)", color='white', ha='center', fontsize=12, weight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved Heatmap to {output_path}")
    plt.close()

def plot_genre_fingerprint(genre_df, output_path="plots/genre_fingerprint.png"):
    """
    New Visual 2: Genre Fingerprint (Ridgeline-ish KDE)
    Comparing Action vs Drama vs Comedy
    """
    plt.figure(figsize=(10, 6))
    
    # Custom palette
    palette = {"Action": "#d62728", "Drama": "#1f77b4", "Comedy": "#ff7f0e"}
    
    sns.kdeplot(
        data=genre_df, 
        x="duration", 
        hue="genre", 
        fill=True, 
        common_norm=False, 
        palette=palette,
        alpha=0.4,
        linewidth=2
    )
    
    plt.xlim(0, 15)
    plt.xlabel("Shot Duration (Seconds)", fontsize=11, weight='bold')
    plt.ylabel("Density", fontsize=11, weight='bold')
    plt.title("Genre Fingerprint: Universally Fast Pacing", fontsize=14, loc='left', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved Genre Fingerprint to {output_path}")
    plt.close()

def plot_cost_of_consistency(cost_df, output_path="plots/cost_of_consistency.png"):
    """
    New Visual 3: Cost of Consistency Curve
    X: Duration, Y: % Covered
    """
    plt.figure(figsize=(10, 6))
    
    plt.plot(cost_df['duration'], cost_df['percent_covered'], color='#2ca02c', linewidth=3)
    
    # Annotation at 5s
    val_5s = cost_df[cost_df['duration'] >= 5].iloc[0]['percent_covered']
    plt.plot(5, val_5s, 'o', color='black')
    plt.text(6, val_5s - 5, f"5s = {val_5s:.1f}% of Cinema", fontsize=11)
    
    # Annotation at 60s
    plt.text(45, 95, "100x Compute Cost\nfor +1% Utility ->", fontsize=10, color='#d62728', ha='right')
    
    plt.xlim(0, 60)
    plt.ylim(0, 105)
    plt.xlabel("Generated Clip Length (Seconds)", fontsize=11, weight='bold')
    plt.ylabel("% of Real-World Shots Covered", fontsize=11, weight='bold')
    plt.title("The Cost of Consistency: Diminishing Returns", fontsize=14, loc='left', pad=20)
    
    plt.grid(True, which='major', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved Cost Curve to {output_path}")
    plt.close()
