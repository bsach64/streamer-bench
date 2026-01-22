#!/usr/bin/env python3
"""
Cedana Performance Visualization Script
Creates grouped bar charts comparing checkpoint, restore, and total times
for different compression methods and stream counts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import argparse
from datetime import datetime


def load_data(csv_file):
    """Load timing data from CSV file."""
    if not os.path.exists(csv_file):
        raise FileNotFoundError(
            f"Timing data file '{csv_file}' not found. Run ./run_benchmarks.sh first."
        )

    df = pd.read_csv(csv_file)
    return df


def prepare_data(df):
    """Prepare data for visualization - calculate min, median, and std."""
    # Group by compression and streams
    grouped = df.groupby(["compression", "streams"])[
        ["checkpoint_time", "restore_time", "total_time"]
    ]

    min_data = grouped.min().reset_index()
    median_data = grouped.median().reset_index()
    std_data = grouped.std().reset_index()

    # Check if we have multiple runs
    df["run_count"] = df.groupby(["compression", "streams"])["compression"].transform(
        "count"
    )
    has_multiple_runs = df["run_count"].iloc[0] > 1

    return min_data, median_data, std_data, has_multiple_runs


def create_min_visualization(min_data, output_prefix="cedana_performance_min"):
    """Create visualization showing only minimum times."""

    # Set up the plotting style
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "Cedana Checkpoint/Restore Performance - Minimum Times",
        fontsize=16,
        fontweight="bold",
    )

    # Colors for the three metrics
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # blue, orange, green

    # Filter data by stream count
    zero_streams = min_data[min_data["streams"] == 0].copy()
    two_streams = min_data[min_data["streams"] == 2].copy()
    four_streams = min_data[min_data["streams"] == 4].copy()
    eight_streams = min_data[min_data["streams"] == 8].copy()

    def plot_grouped_bars(ax, data, title):
        """Plot grouped bars for a single subplot."""
        compressions = data["compression"].values
        x_pos = np.arange(len(compressions))
        bar_width = 0.25

        # Extract the three metrics
        checkpoint_times = data["checkpoint_time"].values
        restore_times = data["restore_time"].values
        total_times = data["total_time"].values

        # Create the bars without error bars
        bars1 = ax.bar(
            x_pos - bar_width,
            checkpoint_times,
            bar_width,
            label="Checkpoint",
            color=colors[0],
            alpha=0.8,
        )
        bars2 = ax.bar(
            x_pos,
            restore_times,
            bar_width,
            label="Restore",
            color=colors[1],
            alpha=0.8,
        )
        bars3 = ax.bar(
            x_pos + bar_width,
            total_times,
            bar_width,
            label="Total",
            color=colors[2],
            alpha=0.8,
        )

        # Add value labels on top of bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    rotation=0,
                )

        # Show value labels above bars
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)

        # Customize the subplot
        ax.set_xlabel("Compression Method", fontsize=12)
        ax.set_ylabel("Time (seconds)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(compressions, fontsize=11)
        ax.legend(loc="upper left", fontsize=11)

        # Add grid for better readability
        ax.grid(True, alpha=0.3)

        # Set y-axis to start from 0
        ax.set_ylim(bottom=0)

        return bars1, bars2, bars3

    # Plot for zero streams
    bars1, bars2, bars3 = plot_grouped_bars(ax1, zero_streams, "0 Streams Performance")

    # Plot for 2 streams
    bars4, bars5, bars6 = plot_grouped_bars(ax2, two_streams, "2 Streams Performance")

    # Plot for 4 streams
    bars7, bars8, bars9 = plot_grouped_bars(ax3, four_streams, "4 Streams Performance")

    # Plot for 8 streams
    bars10, bars11, bars12 = plot_grouped_bars(
        ax4, eight_streams, "8 Streams Performance"
    )

    # Adjust layout and save
    plt.tight_layout()

    # Save in multiple formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # High-resolution PNG
    png_filename = f"{output_prefix}_{timestamp}.png"
    plt.savefig(png_filename, dpi=300, bbox_inches="tight")
    print(f"Saved minimum times PNG: {png_filename}")

    # Also save a generic version without timestamp for easy reference
    generic_png = f"{output_prefix}.png"
    plt.savefig(generic_png, dpi=300, bbox_inches="tight")
    print(f"Saved generic minimum times PNG: {generic_png}")

    # Show the plot
    plt.show()

    return png_filename


def create_median_visualization(
    median_data, std_data, has_multiple_runs, output_prefix="cedana_performance_median"
):
    """Create visualization showing median times with error bars."""

    # Set up the plotting style
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "Cedana Checkpoint/Restore Performance - Median Times with Error Bars",
        fontsize=16,
        fontweight="bold",
    )

    # Colors for the three metrics
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # blue, orange, green

    # Filter data by stream count
    zero_streams = median_data[median_data["streams"] == 0].copy()
    two_streams = median_data[median_data["streams"] == 2].copy()
    four_streams = median_data[median_data["streams"] == 4].copy()
    eight_streams = median_data[median_data["streams"] == 8].copy()

    std_zero = std_data[std_data["streams"] == 0].copy() if has_multiple_runs else None
    std_two = std_data[std_data["streams"] == 2].copy() if has_multiple_runs else None
    std_four = std_data[std_data["streams"] == 4].copy() if has_multiple_runs else None
    std_eight = std_data[std_data["streams"] == 8].copy() if has_multiple_runs else None

    def plot_grouped_bars(ax, data, std_data, title):
        """Plot grouped bars for a single subplot."""
        compressions = data["compression"].values
        x_pos = np.arange(len(compressions))
        bar_width = 0.25

        # Extract the three metrics
        checkpoint_times = data["checkpoint_time"].values
        restore_times = data["restore_time"].values
        total_times = data["total_time"].values

        # Extract standard deviations if available
        checkpoint_err = (
            std_data["checkpoint_time"].values if std_data is not None else None
        )
        restore_err = std_data["restore_time"].values if std_data is not None else None
        total_err = std_data["total_time"].values if std_data is not None else None

        # Create the bars
        bars1 = ax.bar(
            x_pos - bar_width,
            checkpoint_times,
            bar_width,
            label="Checkpoint",
            color=colors[0],
            alpha=0.8,
            yerr=checkpoint_err,
            capsize=5 if checkpoint_err is not None else None,
        )
        bars2 = ax.bar(
            x_pos,
            restore_times,
            bar_width,
            label="Restore",
            color=colors[1],
            alpha=0.8,
            yerr=restore_err,
            capsize=5 if restore_err is not None else None,
        )
        bars3 = ax.bar(
            x_pos + bar_width,
            total_times,
            bar_width,
            label="Total",
            color=colors[2],
            alpha=0.8,
            yerr=total_err,
            capsize=5 if total_err is not None else None,
        )

        # Add value labels on top of bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    rotation=0,
                )

        # Show median value labels, even with error bars
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)

        # Customize the subplot
        ax.set_xlabel("Compression Method", fontsize=12)
        ax.set_ylabel("Time (seconds)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(compressions, fontsize=11)
        ax.legend(loc="upper left", fontsize=11)

        # Add grid for better readability
        ax.grid(True, alpha=0.3)

        # Set y-axis to start from 0
        ax.set_ylim(bottom=0)

        return bars1, bars2, bars3

    # Plot for zero streams
    bars1, bars2, bars3 = plot_grouped_bars(
        ax1, zero_streams, std_zero, "0 Streams Performance"
    )

    # Plot for 2 streams
    bars4, bars5, bars6 = plot_grouped_bars(
        ax2, two_streams, std_two, "2 Streams Performance"
    )

    # Plot for 4 streams
    bars7, bars8, bars9 = plot_grouped_bars(
        ax3, four_streams, std_four, "4 Streams Performance"
    )

    # Plot for 8 streams
    bars10, bars11, bars12 = plot_grouped_bars(
        ax4, eight_streams, std_eight, "8 Streams Performance"
    )

    # Adjust layout and save
    plt.tight_layout()

    # Save in multiple formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # High-resolution PNG
    png_filename = f"{output_prefix}_{timestamp}.png"
    plt.savefig(png_filename, dpi=300, bbox_inches="tight")
    print(f"Saved median times PNG: {png_filename}")

    # Also save a generic version without timestamp for easy reference
    generic_png = f"{output_prefix}.png"
    plt.savefig(generic_png, dpi=300, bbox_inches="tight")
    print(f"Saved generic median times PNG: {generic_png}")

    # Show the plot
    plt.show()

    return png_filename


def create_table_border(widths, style="header"):
    """Create Unicode table border lines."""
    if style == "header":
        return "┌" + "┬".join("─" * w for w in widths) + "┐"
    elif style == "separator":
        return "├" + "┼".join("─" * w for w in widths) + "┤"
    elif style == "footer":
        return "└" + "┴".join("─" * w for w in widths) + "┘"


def format_table_row(values, widths, alignments=None):
    """Format a table row with proper alignment."""
    if alignments is None:
        alignments = ["left"] * len(values)

    formatted_values = []
    for i, (value, width, align) in enumerate(zip(values, widths, alignments)):
        if align == "center":
            formatted_values.append(f"{str(value):^{width}}")
        elif align == "right":
            formatted_values.append(f"{str(value):>{width}}")
        else:  # left
            formatted_values.append(f"{str(value):<{width}}")

    return "│" + "│".join(formatted_values) + "│"


def generate_summary_report(df, min_data, median_data):
    """Generate a text summary report for both minimum and median times."""
    print("\n" + "=" * 70)
    print("CEDANA PERFORMANCE SUMMARY REPORT")
    print("=" * 70)

    print(f"\nTotal tests run: {len(df)}")
    print(f"Configurations tested: {len(min_data)}")

    # Minimum Times Analysis
    print("\n" + "-" * 50)
    print("MINIMUM TIMES ANALYSIS (Best Case Performance)")
    print("-" * 50)

    # Find best performers (minimum times)
    best_checkpoint_min = min_data.loc[min_data["checkpoint_time"].idxmin()]
    best_restore_min = min_data.loc[min_data["restore_time"].idxmin()]
    best_total_min = min_data.loc[min_data["total_time"].idxmin()]

    print(
        f"\nBest checkpoint time: {best_checkpoint_min['compression']} with {best_checkpoint_min['streams']} streams ({best_checkpoint_min['checkpoint_time']:.3f}s)"
    )
    print(
        f"Best restore time: {best_restore_min['compression']} with {best_restore_min['streams']} streams ({best_restore_min['restore_time']:.3f}s)"
    )
    print(
        f"Best total time: {best_total_min['compression']} with {best_total_min['streams']} streams ({best_total_min['total_time']:.3f}s)"
    )

    # Median Times Analysis
    print("\n" + "-" * 50)
    print("MEDIAN TIMES ANALYSIS (Typical Performance)")
    print("-" * 50)

    # Find best performers (median times)
    best_checkpoint_med = median_data.loc[median_data["checkpoint_time"].idxmin()]
    best_restore_med = median_data.loc[median_data["restore_time"].idxmin()]
    best_total_med = median_data.loc[median_data["total_time"].idxmin()]

    print(
        f"\nBest checkpoint time: {best_checkpoint_med['compression']} with {best_checkpoint_med['streams']} streams ({best_checkpoint_med['checkpoint_time']:.3f}s)"
    )
    print(
        f"Best restore time: {best_restore_med['compression']} with {best_restore_med['streams']} streams ({best_restore_med['restore_time']:.3f}s)"
    )
    print(
        f"Best total time: {best_total_med['compression']} with {best_total_med['streams']} streams ({best_total_med['total_time']:.3f}s)"
    )

    # Stream Performance Comparison
    print("\n" + "-" * 50)
    print("STREAM PERFORMANCE COMPARISON")
    print("-" * 50)

    stream_counts = [0, 2, 4, 8]
    min_times = {}
    med_times = {}

    # Define table structure
    col_widths = [9, 12, 12, 12]
    col_alignments = ["center", "right", "right", "right"]
    headers = ["Streams", "Min Time(s)", "Median(s)", "Variance(%)"]

    # Print table with Unicode borders
    print(create_table_border(col_widths, "header"))
    print(format_table_row(headers, col_widths, ["center"] * 4))
    print(create_table_border(col_widths, "separator"))

    for streams in stream_counts:
        if streams in min_data["streams"].values:
            stream_min = min_data[min_data["streams"] == streams]["total_time"].mean()
            stream_med = median_data[median_data["streams"] == streams][
                "total_time"
            ].mean()
            min_times[streams] = stream_min
            med_times[streams] = stream_med
            diff_pct = (
                ((stream_med - stream_min) / stream_min * 100) if stream_min > 0 else 0
            )

            row_values = [
                f"{streams:^7}",  # Centered stream count
                f"{stream_min:>9.3f}",  # Right-aligned min time
                f"{stream_med:>9.3f}",  # Right-aligned median time
                f"{diff_pct:>8.1f}",  # Right-aligned percentage
            ]
            print(format_table_row(row_values, col_widths, col_alignments))

    print(create_table_border(col_widths, "footer"))

    # Calculate speedups relative to 0 streams
    print(f"\nSpeedup Analysis (relative to 0 streams):")
    if 0 in min_times and min_times[0] > 0:
        min_baseline = min_times[0]
        med_baseline = med_times[0]

        # Define speedup table structure
        speedup_widths = [9, 11, 11]
        speedup_alignments = ["center", "right", "right"]
        speedup_headers = ["Streams", "Min Speedup", "Median Spd."]

        print(create_table_border(speedup_widths, "header"))
        print(format_table_row(speedup_headers, speedup_widths, ["center"] * 3))
        print(create_table_border(speedup_widths, "separator"))

        for streams in [2, 4, 8]:
            if streams in min_times and streams in med_times:
                min_speedup = (min_baseline - min_times[streams]) / min_baseline * 100
                med_speedup = (med_baseline - med_times[streams]) / med_baseline * 100

                # Format with + for positive values
                min_formatted = f"{min_speedup:+6.1f}%"
                med_formatted = f"{med_speedup:+6.1f}%"

                row_values = [
                    f"{streams:^7}",
                    f"{min_formatted:>10}",
                    f"{med_formatted:>10}",
                ]
                print(format_table_row(row_values, speedup_widths, speedup_alignments))

        print(create_table_border(speedup_widths, "footer"))
    else:
        print("Speedup calculations: N/A")

    # Compression method comparison
    print("\n" + "-" * 50)
    print("COMPRESSION METHOD RANKING")
    print("-" * 50)

    # Create combined compression method comparison table
    comp_summary_min = min_data.groupby("compression")["total_time"].mean()
    comp_summary_med = median_data.groupby("compression")["total_time"].mean()

    # Define compression table structure
    comp_widths = [13, 12, 12]
    comp_alignments = ["left", "right", "right"]
    comp_headers = ["Method", "Min Time(s)", "Median(s)"]

    print(create_table_border(comp_widths, "header"))
    print(format_table_row(comp_headers, comp_widths, ["center", "center", "center"]))
    print(create_table_border(comp_widths, "separator"))

    # Get all compression methods and sort by median performance
    all_methods = set(comp_summary_min.index) | set(comp_summary_med.index)
    sorted_methods = sorted(
        all_methods, key=lambda x: comp_summary_med.get(x, float("inf"))
    )

    for method in sorted_methods:
        min_time = comp_summary_min.get(method, 0)
        med_time = comp_summary_med.get(method, 0)

        row_values = [f"{method:<12}", f"{min_time:>10.3f}", f"{med_time:>10.3f}"]
        print(format_table_row(row_values, comp_widths, comp_alignments))

    print(create_table_border(comp_widths, "footer"))

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Cedana performance visualization"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="timing_results.csv",
        help="Input CSV file with timing data (default: timing_results.csv)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="cedana_performance",
        help="Output file prefix (default: cedana_performance)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only show plots, suppress summary report",
    )

    args = parser.parse_args()

    try:
        # Load and prepare data
        df = load_data(args.input)
        min_data, median_data, std_data, has_multiple_runs = prepare_data(df)

        if not args.quiet:
            generate_summary_report(df, min_data, median_data)

        # Create both visualizations
        print("\nGenerating minimum times visualization...")
        png_min = create_min_visualization(min_data, args.output + "_min")

        print("\nGenerating median times visualization...")
        png_median = create_median_visualization(
            median_data, std_data, has_multiple_runs, args.output + "_median"
        )

        print(f"\nVisualization complete!")
        print(f"Minimum times PNG: {png_min}")
        print(f"Median times PNG: {png_median}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
