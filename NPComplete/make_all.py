"""Generate NP-Complete benchmark results, figures, and LaTeX appendix assets."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pandas is required; install with `pip install pandas`.") from exc

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: F401
except ImportError as exc:  # pragma: no cover
    raise SystemExit("matplotlib is required; install with `pip install matplotlib`.") from exc

try:
    from NPComplete import benchmark
except ImportError:  # pragma: no cover
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from NPComplete import benchmark


def ensure_results(csv_path: Path) -> None:
    """Run default benchmarks if results.csv is missing."""

    if csv_path.exists():
        return
    df = benchmark.run_benchmarks(
        sizes=[10, 20, 50, 100], m=3, replicates=5, base_seed=12345
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    figures_dir = csv_path.parent.parent / "figures"
    benchmark.plot_runtime(df, figures_dir)
    benchmark.plot_cover_sizes(df, figures_dir)


def build_figs_tex(figs_path: Path) -> None:
    """Write LaTeX figures include file."""

    content = """\\begin{figure}[!t]
    \\centering
    \\includegraphics[width=\\linewidth]{NPComplete/figures/vc_runtime.png}
    \\caption{Vertex-cover runtime on BA PPI networks}
    \\label{fig:np-vc-runtime}
\\end{figure}

\\begin{figure}[!t]
    \\centering
    \\includegraphics[width=\\linewidth]{NPComplete/figures/vc_cover_size.png}
    \\caption{Vertex-cover sizes (greedy vs optimal for small n)}
    \\label{fig:np-vc-size}
\\end{figure}
"""
    figs_path.parent.mkdir(parents=True, exist_ok=True)
    figs_path.write_text(content, encoding="utf-8")


def build_tables_tex(csv_path: Path, table_path: Path) -> None:
    """Compute summary statistics and write LaTeX table."""

    df = pd.read_csv(csv_path)
    rows: List[str] = []
    for n in sorted(df["n"].unique()):
        edge_subset = df[(df["n"] == n) & (df["alg_name"] == "edge_2approx")]
        degree_subset = df[(df["n"] == n) & (df["alg_name"] == "degree_greedy")]

        edge_mean = edge_subset["cover_size"].mean()
        degree_mean = degree_subset["cover_size"].mean()

        edge_ratio = edge_subset["approx_ratio"].dropna()
        degree_ratio = degree_subset["approx_ratio"].dropna()

        edge_ratio_mean = edge_ratio.mean() if not edge_ratio.empty else None
        degree_ratio_mean = degree_ratio.mean() if not degree_ratio.empty else None

        edge_ratio_str = f"{edge_ratio_mean:.3f}" if edge_ratio_mean is not None else "-"
        degree_ratio_str = f"{degree_ratio_mean:.3f}" if degree_ratio_mean is not None else "-"

        edge_mean_str = f"{edge_mean:.2f}" if edge_mean == edge_mean else "-"
        degree_mean_str = f"{degree_mean:.2f}" if degree_mean == degree_mean else "-"

        rows.append(f"{n} & {edge_mean_str} & {degree_mean_str} & {edge_ratio_str} & {degree_ratio_str} \\\\")

    table_content = """\\begin{table}[!t]
    \\centering
    \\caption{Vertex-cover summary statistics on BA PPI networks}
    \\label{tab:np-vc-summary}
    \\begin{tabular}{rcccc}
        n & edge\\_mean & degree\\_mean & edge\\_ratio\\_mean & degree\\_ratio\\_mean \\\\
        \\hline
        %s
    \\end{tabular}
\\end{table}
""" % ("\n        ".join(rows))

    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text(table_content, encoding="utf-8")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    figures_dir = base_dir / "figures"
    appendix_dir = base_dir / "appendix"

    csv_path = results_dir / "results.csv"
    ensure_results(csv_path)

    # Regenerate plots in case results existed but plots missing/stale.
    df = pd.read_csv(csv_path)
    benchmark.plot_runtime(df, figures_dir)
    benchmark.plot_cover_sizes(df, figures_dir)

    figs_path = appendix_dir / "figs.tex"
    build_figs_tex(figs_path)

    tables_path = appendix_dir / "tables.tex"
    build_tables_tex(csv_path, tables_path)

    for path in [
        csv_path,
        figures_dir / "vc_runtime.png",
        figures_dir / "vc_cover_size.png",
        appendix_dir / "figs.tex",
        appendix_dir / "tables.tex",
    ]:
        print(f"WROTE: {path.resolve()}")


if __name__ == "__main__":
    main()
