import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

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
    """
    Visual 1: The 'Barcode' Timeline
    Horizontal strip where every vertical black line is a cut.
    """
    # Create cumulative time to plot cut points
    bourne_df = bourne_df.sort_values('shot_number')
    bourne_df['end_time'] = bourne_df['shot_length_sec'].cumsum()
    
    # We only want to show 10 minutes to make it legible (or full movie if it fits)
    # 10 minutes = 600 seconds.
    subset = bourne_df[bourne_df['end_time'] <= 600]
    
    plt.figure(figsize=(12, 3))
    ax = plt.gca()
    
    # Draw vertical line for each cut
    for cut_point in subset['end_time']:
        ax.axvline(x=cut_point, color='black', linewidth=0.8, alpha=0.9)
        
    ax.set_yticks([])
    ax.set_xlim(0, 600)
    ax.set_xlabel("Time (Seconds) - First 10 Minutes")
    ax.set_title("Visualizing Cut Density: 'The Bourne Ultimatum'", fontsize=14, pad=15, loc='left')
    
    # Add caption annotation
    plt.figtext(0.13, -0.1, "Each line represents a hard cut. 98% of cuts occur < 4s apart.", fontsize=10, style='italic')
    
    sns.despine(left=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved Barcode to {output_path}")
    plt.close()

def plot_cumulative_density(mb_df, output_path="plots/cumulative_density.png"):
    """
    Visual 2: The '95% Threshold' CDF
    Line graph, 0-30s, bold red line at 14.8s.
    """
    plt.figure(figsize=(10, 6))
    
    # Calculate CDF manually for cleaner plotting control or use seaborn ecdf
    sns.ecdfplot(data=mb_df, x="duration", color="#333333", linewidth=2.5, label="All Cinema (MovieBench)")
    
    # Add Marker
    p95 = mb_df['duration'].quantile(0.95) # Should be ~14.8
    plt.axvline(x=p95, color='#d62728', linestyle='--', linewidth=2, label=f"95% Threshold ({p95:.1f}s)")
    plt.axhline(y=0.95, color='#d62728', linestyle=':', linewidth=1)
    
    plt.xlim(0, 30)
    plt.ylim(0, 1.05)
    plt.xlabel("Shot Duration (Seconds)", fontsize=11, weight='bold')
    plt.ylabel("Cumulative % of Shots", fontsize=11, weight='bold')
    plt.title("The Consistency Gap: 95% of Cinema is < 15 Seconds", fontsize=14, loc='left', pad=20)
    
    plt.legend(frameon=False, loc='lower right')
    
    # Annotate "Diminishing Returns"
    plt.text(16, 0.5, "Diminishing Returns\nfor GenAI Capability", fontsize=10, color='#666666')
    plt.arrow(15.5, 0.6, 5, 0, head_width=0.03, color='#666666')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved CDF to {output_path}")
    plt.close()

def plot_ceiling_scatter(blockbuster_df, output_path="plots/distribution_histogram.png"):
    """
    Visual 3: The 'Ceiling' Scatter (actually replacing histogram as per user req for visual 3)
    Scatter plot of "Top 20 Blockbusters".
    X-Axis: Movie Title. Y-Axis: Median Shot Length.
    """
    # Clean up titles for display
    blockbuster_df['short_title'] = blockbuster_df['title'].apply(lambda x: x.split(':')[0][:20])
    
    plt.figure(figsize=(12, 6))
    
    # Plot
    # Sort by median shot length
    blockbuster_df = blockbuster_df.sort_values('median_shot')
    
    sns.scatterplot(data=blockbuster_df, x='short_title', y='median_shot', s=100, color='#1f77b4', zorder=10)
    
    # Add stems (lollipop chart look)
    plt.vlines(x=blockbuster_df['short_title'], ymin=0, ymax=blockbuster_df['median_shot'], color='#1f77b4', alpha=0.4, linewidth=1)
    
    plt.axhline(y=5, color='#d62728', linestyle='--', linewidth=1.5, label='5s Soft Ceiling')
    
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.ylabel("Median Shot Length (s)", fontsize=11, weight='bold')
    plt.xlabel("") # Titles are self explanatory
    plt.title("Blockbuster Pacing: The 3-5 Second Standard", fontsize=14, loc='left', pad=20)
    
    plt.ylim(0, 6) # Zoom in
    plt.legend(frameon=False)
    
    sns.despine()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved Scatter to {output_path}")
    plt.close()

