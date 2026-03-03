#!/usr/bin/env python3
"""Plot old-v-new checkpoint/restore timings as grouped stacked bars."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_and_pick(csv_path: Path, streams: int, compressions: list[str]) -> pd.DataFrame:
    """Load one CSV and return one row per compression for the selected stream count."""
    df = pd.read_csv(csv_path)
    picked = df[df["streams"] == streams].copy()

    # Support multiple runs by averaging each metric per compression.
    picked = (
        picked.groupby("compression", as_index=False)[
            ["checkpoint_time", "restore_time", "total_time"]
        ]
        .mean()
        .set_index("compression")
        .reindex(compressions)
        .reset_index()
    )

    if picked[["checkpoint_time", "restore_time", "total_time"]].isna().any().any():
        missing = picked[picked["checkpoint_time"].isna()]["compression"].tolist()
        raise ValueError(f"Missing compression rows in {csv_path}: {missing}")

    return picked


def plot_for_stream(
    base: Path,
    compressions: list[str],
    target_stream: int,
    dataset_prefix: str,
    dataset_label: str,
    workload: str,
) -> Path:
    """Create one grouped stacked chart for a target stream and return output path."""
    out = (
        base
        / f"{dataset_prefix}_{workload}_checkpoint_restore_grouped_{target_stream}streams.png"
    )

    scenarios = [
        ("0 streams", base / f"{dataset_prefix}_{workload}.csv", 0),
        (
            f"{target_stream} streams (no mem limit)",
            base / f"{dataset_prefix}_{workload}.csv",
            target_stream,
        ),
        (
            f"{target_stream} streams (1000MB)",
            base / f"{dataset_prefix}_{workload}_1000MB.csv",
            target_stream,
        ),
        (
            f"{target_stream} streams (250MB)",
            base / f"{dataset_prefix}_{workload}_250MB.csv",
            target_stream,
        ),
        (
            f"{target_stream} streams (100MB)",
            base / f"{dataset_prefix}_{workload}_100MB.csv",
            target_stream,
        ),
    ]

    # shape: [scenario_idx][compression_idx]
    checkpoint_vals = []
    restore_vals = []
    total_vals = []

    for _, csv_path, streams in scenarios:
        picked = load_and_pick(csv_path, streams, compressions)
        checkpoint_vals.append(picked["checkpoint_time"].to_numpy())
        restore_vals.append(picked["restore_time"].to_numpy())
        total_vals.append(picked["total_time"].to_numpy())

    checkpoint_vals = np.array(checkpoint_vals)
    restore_vals = np.array(restore_vals)
    total_vals = np.array(total_vals)

    fig, ax = plt.subplots(figsize=(16, 8))

    x = np.arange(len(scenarios))
    n_comp = len(compressions)
    group_width = 0.82
    bar_width = group_width / n_comp
    offsets = (np.arange(n_comp) - (n_comp - 1) / 2) * bar_width

    checkpoint_color = "#4C78A8"
    restore_color = "#F58518"

    max_total = float(np.max(total_vals))
    label_offset = max(0.02, max_total * 0.015)

    for j, comp in enumerate(compressions):
        xpos = x + offsets[j]
        cp = checkpoint_vals[:, j]
        rs = restore_vals[:, j]
        totals = total_vals[:, j]

        ax.bar(
            xpos,
            cp,
            width=bar_width * 0.95,
            color=checkpoint_color,
            edgecolor="black",
            linewidth=0.5,
            label="checkpoint" if j == 0 else None,
        )
        ax.bar(
            xpos,
            rs,
            width=bar_width * 0.95,
            bottom=cp,
            color=restore_color,
            edgecolor="black",
            linewidth=0.5,
            label="restore" if j == 0 else None,
        )

        for xi, total in zip(xpos, totals):
            ax.text(
                xi,
                total + label_offset,
                f"{total:.2f}s",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=90,
            )

    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _, _ in scenarios], fontsize=10)
    ax.set_ylabel("Time (seconds)")
    ax.set_xlabel("Scenario")
    ax.set_title(
        f"{dataset_label} ({workload}): Checkpoint + Restore Time by Compression ({target_stream} streams)"
    )
    ax.set_ylim(0, max_total * 1.35)
    ax.grid(axis="y", alpha=0.25)

    legend_comp = [
        plt.Line2D([0], [0], color="none", label=f"{i+1}: {c}")
        for i, c in enumerate(compressions)
    ]
    leg1 = ax.legend(
        title="Stack Colors",
        loc="lower left",
        bbox_to_anchor=(x[0] - group_width / 2, max_total * 1.07),
        bbox_transform=ax.transData,
    )
    ax.add_artist(leg1)
    ax.legend(handles=legend_comp, title="Bar Order in Each Group", loc="upper right")

    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    base = Path("results/old-v-new")
    compressions = ["none", "tar", "gzip", "lz4", "zlib"]
    datasets = [("local", "Local"), ("cedana", "Cedana")]
    workloads = ["stress_py", "cuda_stress"]

    for workload in workloads:
        for dataset_prefix, dataset_label in datasets:
            for target_stream in (2, 4, 8):
                out = plot_for_stream(
                    base,
                    compressions,
                    target_stream,
                    dataset_prefix,
                    dataset_label,
                    workload,
                )
                print(f"Saved: {out}")


if __name__ == "__main__":
    main()
