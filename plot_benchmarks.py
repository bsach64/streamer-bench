import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def load_data():
    local_df = pd.read_csv("results/3_runs_local.csv")
    s3_df = pd.read_csv("results/3_runs_s3.csv")
    cedana_df = pd.read_csv("results/3_runs_cedana_storage_timings.csv")

    local_df["storage"] = "local"
    s3_df["storage"] = "s3"
    cedana_df["storage"] = "cedana"

    return pd.concat([local_df, s3_df, cedana_df], ignore_index=True)


def calculate_stats(df):
    stats = []
    for compression in df["compression"].unique():
        for streams in df["streams"].unique():
            for storage in ["local", "s3", "cedana"]:
                subset = df[
                    (df["compression"] == compression)
                    & (df["streams"] == streams)
                    & (df["storage"] == storage)
                ]

                if len(subset) > 0:
                    for stat_type, func in [("min", np.min), ("median", np.median)]:
                        stats.append(
                            {
                                "compression": compression,
                                "streams": streams,
                                "storage": storage,
                                "stat_type": stat_type,
                                "checkpoint_time": func(subset["checkpoint_time"]),
                                "restore_time": func(subset["restore_time"]),
                                "total_time": func(subset["total_time"]),
                            }
                        )

    return pd.DataFrame(stats)


def plot_graph(stats_df, stat_type):
    compressions = sorted(stats_df["compression"].unique())
    streams = [0, 2, 4, 8]
    storages = ["local", "s3", "cedana"]

    storage_colors = {"local": "#4CAF50", "s3": "#2196F3", "cedana": "#FF9800"}

    checkpoint_color = "#90EE90"
    restore_color = "#FFB6C1"

    n_compressions = len(compressions)
    fig, axes = plt.subplots(n_compressions, 1, figsize=(14, 5 * n_compressions))

    if n_compressions == 1:
        axes = [axes]

    for idx, compression in enumerate(compressions):
        ax = axes[idx]

        comp_data = stats_df[
            (stats_df["compression"] == compression)
            & (stats_df["stat_type"] == stat_type)
        ]

        x = np.arange(len(streams))
        width = 0.25

        for i, storage in enumerate(storages):
            checkpoint_vals = []
            restore_vals = []

            for stream in streams:
                storage_stream_data = comp_data[
                    (comp_data["storage"] == storage) & (comp_data["streams"] == stream)
                ]
                if len(storage_stream_data) > 0:
                    checkpoint_vals.append(
                        storage_stream_data["checkpoint_time"].values[0]
                    )
                    restore_vals.append(storage_stream_data["restore_time"].values[0])
                else:
                    checkpoint_vals.append(0)
                    restore_vals.append(0)

            bar_pos = x + i * width
            p1 = ax.bar(
                bar_pos,
                checkpoint_vals,
                width,
                label=f"{storage} (checkpoint)",
                color=checkpoint_color,
                edgecolor=storage_colors[storage],
                linewidth=2,
            )
            p2 = ax.bar(
                bar_pos,
                restore_vals,
                width,
                bottom=checkpoint_vals,
                label=f"{storage} (restore)",
                color=restore_color,
                edgecolor=storage_colors[storage],
                linewidth=2,
            )

            for j, (cp_val, rs_val) in enumerate(zip(checkpoint_vals, restore_vals)):
                total = cp_val + rs_val
                if total > 0:
                    ax.text(
                        bar_pos[j],
                        total,
                        f"{storage}:{total:.1f}s",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        fontweight="bold",
                    )

        ax.set_xlabel("Number of Streams")
        ax.set_ylabel("Time (seconds)")
        ax.set_title(
            f"Compression: {compression.upper()} - {stat_type.capitalize()} Time"
        )
        ax.set_xticks(x + width)
        ax.set_xticklabels([str(s) for s in streams])

        handles, labels = ax.get_legend_handles_labels()
        by_label = {}
        for handle, label in zip(handles, labels):
            if "checkpoint" in label:
                storage = label.replace(" (checkpoint)", "")
                if "checkpoint" not in by_label:
                    by_label[f"{storage} (checkpoint)"] = handle
            elif "restore" in label:
                storage = label.replace(" (restore)", "")
                if "restore" not in by_label:
                    by_label[f"{storage} (restore)"] = handle

        ax.legend(by_label.values(), by_label.keys(), loc="upper left")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    output_file = f"plots/stream_benchmarks_{stat_type}_v2.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Saved {output_file}")
    plt.close()


def main():
    df = load_data()
    stats_df = calculate_stats(df)

    for stat_type in ["min", "median"]:
        plot_graph(stats_df, stat_type)


if __name__ == "__main__":
    main()
