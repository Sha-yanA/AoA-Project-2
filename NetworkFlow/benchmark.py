"""Benchmarking utilities for organ transplant network flow."""

from __future__ import annotations

import csv
import math
import platform
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

# Handle imports whether run as script or module
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from organ_transplant_flow import OrganTransplantNetworkFlow, generate_transplant_case


def _ensure_dirs() -> tuple[Path, Path]:
    """Create output directories."""
    root = Path(__file__).resolve().parent
    figures = root / "figures"
    results = root / "results"
    figures.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    return figures, results


def _median_time(func, *args, repeats: int = 5) -> float:
    """Measure median execution time over multiple runs."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        func(*args)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def _write_csv(
    path: Path, headers: Iterable[str], rows: Iterable[Iterable[object]]
) -> None:
    """Write CSV file with headers and rows."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def _save_environment_report(results_dir: Path) -> None:
    """Save execution environment information."""
    from datetime import timezone
    
    info = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    path = results_dir / "environment.txt"
    with path.open("w", encoding="utf-8") as handle:
        for key, value in info.items():
            handle.write(f"{key}: {value}\n")


def _build_reference_curve(
    scale_point: tuple[int, float],
    xs: List[int],
    transform,
) -> List[float]:
    """Build theoretical complexity reference curve."""
    n0, t0 = scale_point
    denom = transform(n0)
    coeff = t0 / denom if denom else 0.0
    return [coeff * transform(x) for x in xs]


def run_runtime_benchmarks(figures: Path, results: Path) -> None:
    """Measure runtime scaling and validate O(VE^2) complexity."""
    sizes = [5, 10, 15, 20, 25, 30, 35, 40]
    repeats = 5
    
    records = []
    transplants = []
    iterations = []
    
    for idx, n in enumerate(sizes):
        donors, recipients = generate_transplant_case(n, n, seed=idx)
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        
        start = time.perf_counter()
        max_flow, matches, iters = solver.ford_fulkerson_edmonds_karp()
        elapsed = time.perf_counter() - start
        
        records.append((n, elapsed))
        transplants.append(max_flow)
        iterations.append(iters)
        
        print(f"n={n:2d}: time={elapsed:.4f}s, transplants={max_flow:2d}, iterations={iters:3d}")
    
    _write_csv(results / "times.csv", ("n", "seconds"), records)
    _write_csv(results / "transplants.csv", ("n", "successful"), zip(sizes, transplants))
    _write_csv(results / "iterations.csv", ("n", "iterations"), zip(sizes, iterations))
    
    # Build O(VE^2) reference curve
    if records:
        def complexity(n):
            V = 2 * n + 2
            E = n + n * n + n
            return V * E * E
        
        reference = _build_reference_curve(records[0], sizes, complexity)
    else:
        reference = [0.0 for _ in sizes]
    
    # Plot runtime
    _plot_runtime(
        sizes,
        [t for _, t in records],
        reference,
        figures / "runtime_vs_n.png",
        figures / "runtime_vs_n.pdf",
        title="Organ Transplant Network Flow: Runtime vs Size",
        ylabel="seconds",
        legend=("measured", "c · VE²"),
    )
    
    # Plot successful transplants
    plt.figure(figsize=(6, 4))
    plt.plot(sizes, transplants, marker='s', color='green')
    plt.xlabel('network size (n donors, n recipients)')
    plt.ylabel('successful transplants')
    plt.title('Transplant Success Rate')
    plt.tight_layout()
    plt.savefig(figures / "transplants_vs_n.png", dpi=200)
    plt.savefig(figures / "transplants_vs_n.pdf")
    plt.close()


def _plot_runtime(
    xs: List[int],
    ys: List[float],
    reference: List[float],
    png_path: Path,
    pdf_path: Path,
    title: str,
    ylabel: str,
    legend: Tuple[str, str],
) -> None:
    """Plot runtime with theoretical reference curve."""
    plt.figure(figsize=(6, 4))
    plt.plot(xs, ys, marker="o", label=legend[0])
    plt.plot(xs, reference, linestyle="--", label=legend[1])
    plt.xlabel("network size (n donors, n recipients)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(png_path, dpi=200)
    plt.savefig(pdf_path)
    plt.close()


def run_compatibility_analysis(figures: Path, results: Path) -> None:
    """Analyze impact of compatibility constraints on matching."""
    n = 30
    patterns = [
        "uniform distribution",
        "realistic distribution",
        "rare type dominant"
    ]
    
    rows = []
    for idx, pattern_name in enumerate(patterns):
        donors, recipients = generate_transplant_case(n, n, seed=40 + idx)
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        success_rate = max_flow / n if n > 0 else 0
        rows.append((pattern_name, n, max_flow, f"{success_rate:.2%}"))
    
    _write_csv(results / "compatibility.csv", 
               ("pattern", "recipients", "successful", "success rate"), 
               rows)


def main() -> None:
    """Run all benchmarks and generate outputs."""
    figures, results = _ensure_dirs()
    run_runtime_benchmarks(figures, results)
    run_compatibility_analysis(figures, results)
    _save_environment_report(results)
    print("Benchmarks complete. Results saved to 'results/' and 'figures/' directories.")


if __name__ == "__main__":
    main()