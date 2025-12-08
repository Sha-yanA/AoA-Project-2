# AoA Project 2: Computational Biology Applications

Analysis of Algorithms Project 2: Applying network flow and NP-complete algorithms to real-world biological problems.

## Overview

This project demonstrates two fundamental algorithmic techniques applied to critical problems in computational biology:

1. **Network Flow**: Organ transplant matching optimization
2. **NP-Complete**: {placeholder}

## Project Structure

```
AoA-Project-2/
├── NetworkFlow/              # Problem 1: Organ Transplant Matching
│   ├── organ_transplant_flow.py   # Main implementation
│   ├── benchmark.py               # Performance benchmarking
│   ├── export_appendix.py         # LaTeX generation
│   ├── validation.py              # Correctness validation
│   ├── test_all.py                # Test suite (9 tests)
│   ├── __init__.py
│   ├── requirements.txt
│   ├── README.md
│   ├── appendix/                  # Generated LaTeX files
│   ├── figures/                   # Generated plots
│   └── results/                   # Generated CSV data
│
├── NPComplete/              # Problem 2: Protein Network Analysis
│   ├── {placeholder}.py         # Main implementation
|
│
└── README.md                # This file
```

## Problems Solved

### Problem 1: Organ Transplant Network Flow

**Challenge**: Maximize successful organ transplants while respecting medical compatibility constraints.

**Approach**: Model as maximum flow problem
- **Algorithm**: Ford-Fulkerson with Edmonds-Karp (BFS)
- **Complexity**: O(VE²) = O(n³m²) for n donors, m recipients
- **Result**: Optimal polynomial-time solution

**Key Features**:
- Blood type compatibility (ABO system)
- Tissue marker matching (HLA)
- Donor capacity constraints
- Guaranteed optimal allocation

**Files**:
- `organ_transplant_flow.py` - Main algorithm
- `validation.py` - Medical constraint checking
- `test_all.py` - 9 comprehensive tests

**See**: `NetworkFlow/README.md` for detailed documentation

### Problem 2: {placeholder}


**See**: `NPComplete/README.md` for detailed documentation

## Quick Start

### Installation

```bash
# Clone/navigate to project directory
cd AoA-Project-2

# Install dependencies for both problems
pip install -r NetworkFlow/requirements.txt
pip install -r NPComplete/requirements.txt
```

### Running Tests

```bash
# Network Flow tests (9 tests)
python NetworkFlow/test_all.py

# NP-Complete tests (10 tests)
python NPComplete/test_all.py
```

Expected output: All tests pass ✅

### Running Benchmarks

```bash
# Network Flow benchmarks
cd NetworkFlow
python benchmark.py          # Generates figures/ and results/
python export_appendix.py    # Generates appendix/ LaTeX files
cd ..

# NP-Complete benchmarks
cd NPComplete
python benchmark.py          # Generates figures/ and results/
python export_appendix.py    # Generates appendix/ LaTeX files
cd ..
```

### Compiling LaTeX Report

```bash
# Compile IEEE format report
pdflatex AoAProject2.tex
bibtex AoAProject2
pdflatex AoAProject2.tex
pdflatex AoAProject2.tex
```

## Algorithm Summary

| Problem | Algorithm | Time | Approx | Optimal? | Validated? |
|---------|-----------|------|--------|----------|------------|
| Network Flow | Ford-Fulkerson (Edmonds-Karp) | O(VE²) | Exact | ✅ Yes | ✅ 9 tests |


## Testing & Validation

### Comprehensive Test Suites

**NetworkFlow** (9 tests):
- Perfect matching scenarios
- Capacity constraints
- Blood type incompatibility
- Tissue marker incompatibility
- Empty cases
- Random validation (10 seeds)
- Flow conservation
- Utility functions



### Validation Utilities

**NetworkFlow**:
- `validate_matching()` - Medical constraint checking
- `count_compatible_pairs()` - Compatibility analysis
- `analyze_network_structure()` - Network statistics



## Biological Context

### Why These Problems Matter

**Organ Transplantation**:
- ~100,000 patients on US transplant waiting list
- ~40,000 transplants performed annually
- Optimal allocation saves lives
- Real systems (UNOS) use similar algorithms



### Real-World Impact

Both algorithms have direct applications:

1. **Network Flow → UNOS**: United Network for Organ Sharing uses optimization algorithms for allocation

## Experimental Results

### Network Flow Performance

- **Runtime**: Closely matches O(VE²) theoretical bound
- **Scalability**: Handles networks up to 40 donors/recipients efficiently
- **Success Rate**: 60-80% of recipients receive organs (depends on compatibility)
- **Iterations**: Typically 15-25 augmenting paths
- **Validation**: 100% correctness on 9 test cases + random seeds



## Academic Context

This project demonstrates key concepts from Analysis of Algorithms:

1. **Polynomial Reduction**: Bipartite matching → Network flow
2. **Optimal Algorithms**: Ford-Fulkerson guarantees optimal solution
3. **NP-Completeness**: Vertex cover proven NP-Complete via reduction from 3-SAT
4. **Approximation**: Greedy 2-approximation for intractable problem
5. **Empirical Validation**: Experiments confirm theoretical complexity bounds
6. **Correctness Proofs**: Formal validation with comprehensive test suites

## LaTeX Report Structure

The IEEE format report includes:

- **Abstract**: Project overview
- **Introduction**: Biological context and motivation
- **Problem 1**: Network flow formulation, algorithm, proof, experiments
- **Problem 2**: NP-completeness proof, approximation algorithms, experiments
- **Appendix**: Complete Python implementations, benchmarking code, figures, tables

## File Generation Workflow

```
1. Write Python code (organ_transplant_flow.py, protein_network.py)
   ↓
2. Run tests (test_all.py) → verify correctness ✅
   ↓
3. Run benchmark.py → generates figures/ and results/
   ↓
4. Run export_appendix.py → generates appendix/ LaTeX files
   ↓
5. Compile LaTeX → includes generated appendix files
```

**Key**: Appendix `.tex` files are auto-generated from Python source, maintaining perfect sync between code and documentation.

## Dependencies

- Python >= 3.10
- matplotlib (for plotting)
- Standard library: collections, random, time, pathlib, csv, itertools, unittest

## Testing Best Practices

Both modules follow industry-standard testing:
- ✅ Unit tests for core functionality
- ✅ Edge case handling (empty, small, large)
- ✅ Randomized testing (10+ seeds)
- ✅ Validation against known solutions
- ✅ Medical/biological constraint checking
- ✅ Approximation ratio verification

Run all tests:
```bash
python NetworkFlow/test_all.py && python NPComplete/test_all.py
```

## Extensions

Possible future work:

**Network Flow**:
- Multi-organ transplants
- Paired kidney exchanges
- Geographic constraints
- Priority scoring systems


## References

### Algorithms
- Cormen, T. H., et al. (2022). *Introduction to Algorithms* (4th ed.)
- Ford, L. R., & Fulkerson, D. R. (1956). Maximal flow through a network
- Karp, R. M. (1972). Reducibility among combinatorial problems

### Biology
- Barabási, A. L., & Albert, R. (1999). Emergence of scaling in random networks
- Barabási, A. L., et al. (2011). Network medicine
- Bertsimas, D., et al. (2013). Fairness, efficiency, and flexibility in organ allocation

## Authors

- Shayan Ahmed - shayanahmed@ufl.edu
- Sanjith Devineni - sdevineni@ufl.edu

## Course

Analysis of Algorithms (COT 5405)  
University of Florida  
Fall 2025