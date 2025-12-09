"""Benchmark greedy and exact vertex cover solvers on synthetic PPI networks.

Proteins correspond to vertices and interactions correspond to edges; a vertex
cover is a minimal drug-target set blocking every interaction. Algorithms:
edge-based 2-approximation (O(V + E)), degree-based greedy (O(V^2 + E)), and an
exact brute-force solver (O(2^n · poly(n))) for small graphs. Results are
written to CSV with summary plots for inclusion in reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pandas is required; install with `pip install pandas`.") from exc

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise SystemExit("matplotlib is required; install with `pip install matplotlib`.") from exc

try:
    from NPComplete.protein_network import ProteinInteractionNetwork
except ImportError:  # pragma: no cover
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from NPComplete.protein_network import ProteinInteractionNetwork

ALIAS = {
    "edge_2approx": "Edge-based 2-approx",
    "degree_greedy": "Degree-based greedy",
    "optimal": "Optimal (exact for small n)",
}


def generate_seed(base_seed: int, n: int, replicate: int) -> int:
    """Derive deterministic per-run seeds."""

    return base_seed + 1000 * n + replicate


def run_benchmarks(
    sizes: List[int], m: int, replicates: int, base_seed: int
) -> pd.DataFrame:
    """Run benchmarks across graph sizes and replicates, returning a DataFrame."""

    records: List[Dict[str, Any]] = []

    for n in sizes:
        for rep in range(replicates):
            seed = generate_seed(base_seed, n, rep)
            ppi = ProteinInteractionNetwork.from_barabasi_albert(n=n, m=m, seed=seed)
            stats = ppi.stats()
            optimal_size: Optional[int] = None

            if n <= 16:
                start_opt = perf_counter()
                opt_cover = ppi.brute_force_optimal_vertex_cover(max_n=16)
                runtime_ms = (perf_counter() - start_opt) * 1000
                if opt_cover is not None:
                    optimal_size = len(opt_cover)
                    records.append(
                        {
                            "n": n,
                            "m": stats["m"],
                            "replicate": rep,
                            "alg_name": "optimal",
                            "cover_size": optimal_size,
                            "runtime_ms": runtime_ms,
                            "is_cover": True,
                            "optimal_size": optimal_size,
                            "approx_ratio": 1.0,
                        }
                    )

            algorithms = [
                ("edge_2approx", ppi.greedy_vertex_cover_edge_based, {"seed": seed}),
                ("degree_greedy", ppi.greedy_vertex_cover_degree_based, {}),
            ]

            for alg_name, func, kwargs in algorithms:
                start = perf_counter()
                cover = func(**kwargs)
                runtime_ms = (perf_counter() - start) * 1000
                cover_size = len(cover)
                is_cover = ppi.is_vertex_cover(cover)
                approx_ratio = (cover_size / optimal_size) if optimal_size else None
                records.append(
                    {
                        "n": n,
                        "m": stats["m"],
                        "replicate": rep,
                        "alg_name": alg_name,
                        "cover_size": cover_size,
                        "runtime_ms": runtime_ms,
                        "is_cover": is_cover,
                        "optimal_size": optimal_size,
                        "approx_ratio": approx_ratio,
                    }
                )

    return pd.DataFrame(records)


def save_results(df: pd.DataFrame, results_dir: Path) -> Path:
    """Save benchmark results to CSV."""

    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "results.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


def plot_runtime(df: pd.DataFrame, figures_dir: Path) -> Path:
    """Plot runtime (mean ± std) versus n for greedy algorithms."""

    fig, ax = plt.subplots()
    for alg in ["edge_2approx", "degree_greedy"]:
        subset = df[df["alg_name"] == alg]
        grouped = subset.groupby("n")["runtime_ms"].agg(["mean", "std"]).reset_index()
        ax.errorbar(
            grouped["n"],
            grouped["mean"],
            yerr=grouped["std"],
            marker="o",
            capsize=3,
            label=ALIAS[alg],
        )
    ax.set_xlabel("Number of proteins (n)")
    ax.set_ylabel("Runtime (ms)")
    ax.set_title("Vertex cover runtime on BA PPI networks")
    ax.legend()
    fig.tight_layout()
    figures_dir.mkdir(parents=True, exist_ok=True)
    out_path = figures_dir / "vc_runtime.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


def plot_cover_sizes(df: pd.DataFrame, figures_dir: Path) -> Path:
    """Plot cover size (mean ± std) versus n, with optimal where available."""

    fig, ax = plt.subplots()
    approx_means = (
        df[df["approx_ratio"].notna()].groupby("alg_name")["approx_ratio"].mean().to_dict()
    )

    for alg in ["edge_2approx", "degree_greedy"]:
        subset = df[df["alg_name"] == alg]
        grouped = subset.groupby("n")["cover_size"].agg(["mean", "std"]).reset_index()
        label = ALIAS[alg]
        if alg in approx_means:
            label = f"{label} (mean approx {approx_means[alg]:.2f})"
        ax.errorbar(
            grouped["n"],
            grouped["mean"],
            yerr=grouped["std"],
            marker="o",
            capsize=3,
            label=label,
        )

    optimal_subset = df[df["alg_name"] == "optimal"]
    if not optimal_subset.empty:
        grouped_opt = optimal_subset.groupby("n")["cover_size"].mean().reset_index()
        ax.plot(
            grouped_opt["n"],
            grouped_opt["cover_size"],
            marker="s",
            linestyle="--",
            label=ALIAS["optimal"],
        )

    ax.set_xlabel("Number of proteins (n)")
    ax.set_ylabel("Vertex cover size")
    ax.set_title("Vertex cover sizes on BA PPI networks")
    ax.legend()
    fig.tight_layout()
    figures_dir.mkdir(parents=True, exist_ok=True)
    out_path = figures_dir / "vc_cover_size.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


def print_summary(df: pd.DataFrame) -> None:
    """Print per-n averages of cover sizes and approximation ratios."""

    header = "n | edge_size | degree_size | edge_ratio | degree_ratio"
    print(header)
    for n in sorted(df["n"].unique()):
        edge_subset = df[(df["n"] == n) & (df["alg_name"] == "edge_2approx")]
        degree_subset = df[(df["n"] == n) & (df["alg_name"] == "degree_greedy")]

        edge_mean = edge_subset["cover_size"].mean()
        degree_mean = degree_subset["cover_size"].mean()

        edge_ratio = edge_subset["approx_ratio"].dropna()
        degree_ratio = degree_subset["approx_ratio"].dropna()

        edge_ratio_mean = edge_ratio.mean() if not edge_ratio.empty else None
        degree_ratio_mean = degree_ratio.mean() if not degree_ratio.empty else None

        parts = [
            str(n),
            f"{edge_mean:.2f}" if edge_mean == edge_mean else "-",
            f"{degree_mean:.2f}" if degree_mean == degree_mean else "-",
            f"{edge_ratio_mean:.3f}" if edge_ratio_mean is not None else "-",
            f"{degree_ratio_mean:.3f}" if degree_ratio_mean is not None else "-",
        ]
        print(" | ".join(parts))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Benchmark greedy vertex cover solvers on Barabási–Albert PPI graphs."
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[10, 20, 50, 100],
        help="Graph sizes n to benchmark (default: 10 20 50 100).",
    )
    parser.add_argument("--m", type=int, default=3, help="BA attachment parameter m (default: 3).")
    parser.add_argument(
        "--replicates", type=int, default=5, help="Replicates per size (default: 5)."
    )
    parser.add_argument("--base-seed", type=int, default=12345, help="Base seed for deterministic runs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    figures_dir = base_dir / "figures"
    results_dir = base_dir / "results"

    df = run_benchmarks(args.sizes, args.m, args.replicates, args.base_seed)
    save_results(df, results_dir)
    plot_runtime(df, figures_dir)
    plot_cover_sizes(df, figures_dir)
    print_summary(df)


if __name__ == "__main__":
    main()
