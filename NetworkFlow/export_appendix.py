"""Generate LaTeX appendix assets for the network flow project."""

from __future__ import annotations

import sys
from pathlib import Path

# Handle imports whether run as script or module
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


def _read_text(path: Path) -> str:
    """Read text file content."""
    return path.read_text(encoding="utf-8")


def _listing_block(source: Path, caption: str, label: str) -> str:
    """Generate LaTeX listing block for code."""
    code = _read_text(source).rstrip()
    return (
        "\\begin{lstlisting}[caption={"
        + caption
        + "},label={"
        + label
        + "}]\n"
        + code
        + "\n\\end{lstlisting}\n"
    )


def main() -> None:
    """Generate all LaTeX appendix assets."""
    root = Path(__file__).resolve().parent
    appendix = root / "appendix"
    appendix.mkdir(parents=True, exist_ok=True)

    # Generate code listings
    listings = [
        (
            appendix / "code_organ_transplant_flow.tex",
            _listing_block(
                root / "organ_transplant_flow.py",
                "Organ transplant network flow implementation",
                "lst:nf-transplant",
            ),
        ),
        (
            appendix / "code_benchmark.tex",
            _listing_block(
                root / "benchmark.py",
                "Benchmark and plotting harness",
                "lst:nf-benchmark",
            ),
        ),
    ]
    for path, content in listings:
        path.write_text(content, encoding="utf-8")

    # Generate figure references
    figs_content = "\n".join(
        [
            "\\begin{figure}[ht]",
            "\\centering",
            "\\includegraphics[width=\\linewidth]{NetworkFlow/figures/runtime_vs_n.pdf}",
            "\\caption{Measured runtime for organ transplant network flow with reference $O(VE^2)$ curve.}",
            "\\label{fig:nf-runtime}",
            "\\end{figure}",
            "",
            "\\begin{figure}[ht]",
            "\\centering",
            "\\includegraphics[width=\\linewidth]{NetworkFlow/figures/transplants_vs_n.pdf}",
            "\\caption{Number of successful transplants as network size increases.}",
            "\\label{fig:nf-transplants}",
            "\\end{figure}",
            "",
        ]
    )
    (appendix / "figs.tex").write_text(figs_content, encoding="utf-8")

    # Generate tables from results using pgfplotstable (reads CSV directly)
    tables_content = [
        "% Run `python benchmark.py` from within NetworkFlow folder before including these tables.",
        "",
        "\\begin{table}[H]",
        "  \\centering",
        "  \\caption{Network flow runtime (expected O(VE²))}",
        "  \\label{tab:nf-runtime}",
        "  \\pgfplotstabletypeset[",
        "    col sep=comma,",
        "    header=true,",
        "    string type,",
        "    columns={n,seconds},",
        "    columns/n/.style={column name={$n$}},",
        "    columns/seconds/.style={column name={seconds}}",
        "  ]{NetworkFlow/results/times.csv}",
        "\\end{table}",
        "",
        "\\begin{table}[H]",
        "  \\centering",
        "  \\caption{Successful transplants by network size}",
        "  \\label{tab:nf-transplants}",
        "  \\pgfplotstabletypeset[",
        "    col sep=comma,",
        "    header=true,",
        "    string type,",
        "    columns={n,successful},",
        "    columns/n/.style={column name={$n$}},",
        "    columns/successful/.style={column name={transplants}}",
        "  ]{NetworkFlow/results/transplants.csv}",
        "\\end{table}",
        "",
        "\\begin{table}[H]",
        "  \\centering",
        "  \\caption{Algorithm iterations (augmenting paths)}",
        "  \\label{tab:nf-iterations}",
        "  \\pgfplotstabletypeset[",
        "    col sep=comma,",
        "    header=true,",
        "    string type,",
        "    columns={n,iterations},",
        "    columns/n/.style={column name={$n$}},",
        "    columns/iterations/.style={column name={iterations}}",
        "  ]{NetworkFlow/results/iterations.csv}",
        "\\end{table}",
        "",
        "\\begin{table}[H]",
        "  \\centering",
        "  \\caption{Compatibility analysis}",
        "  \\label{tab:nf-compatibility}",
        "  \\pgfplotstabletypeset[",
        "    col sep=comma,",
        "    header=true,",
        "    string type,",
        "    columns={pattern,recipients,successful,success rate},",
        "    columns/pattern/.style={column name={pattern}},",
        "    columns/recipients/.style={column name={recipients}},",
        "    columns/successful/.style={column name={successful}},",
        "    columns/success rate/.style={column name={success rate}}",
        "  ]{NetworkFlow/results/compatibility.csv}",
        "\\end{table}",
        "",
    ]
    (appendix / "tables.tex").write_text("\n".join(tables_content), encoding="utf-8")

    print("LaTeX appendix assets generated in 'appendix/' directory.")


if __name__ == "__main__":
    main()