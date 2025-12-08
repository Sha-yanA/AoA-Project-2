# Network Flow: Organ Transplant Matching

This module implements the network flow half of the Analysis of Algorithms project: optimize organ transplant allocation to maximize successful transplants while respecting medical compatibility constraints.

## Problem Statement

**Real-world problem:** Organ transplantation faces a critical shortage where thousands of patients await organs while available donors must be allocated optimally. The allocation system must consider blood type compatibility (ABO matching), tissue marker compatibility (HLA matching), donor capacity limits, and recipient medical needs. The goal is to maximize the total number of successful transplants while respecting all medical constraints.

**Abstract problem:** Given a bipartite graph with donors on one side and recipients on the other, where edges exist only between medically compatible donor-recipient pairs, find a maximum cardinality matching that respects donor capacity constraints (each donor can provide limited organs) and recipient needs (each recipient needs exactly one organ).

## Algorithms Implemented

1. **Ford-Fulkerson with Edmonds-Karp (O(VE²))**: Maximum flow algorithm using BFS to find augmenting paths
   - Reduces bipartite matching to network flow
   - Constructs flow network with source and sink
   - Guarantees optimal solution in polynomial time

2. **Medical Compatibility Checking**: Validates donor-recipient pairs based on:
   - Blood type compatibility (O can donate to all, AB can only receive from all, etc.)
   - Tissue marker matching (requires ≥50% HLA marker overlap)

3. **Validation Suite**: Comprehensive correctness verification
   - Medical constraint validation
   - Flow conservation checks
   - Network structure analysis

## Setup

- Requires Python >= 3.10
- Dependency: matplotlib (install via `pip install -r "NetworkFlow/requirements.txt"`)

## Quickstart

```bash
# All commands run from project root (AOA-PROJECT-2/)

# Run tests
python NetworkFlow/test_all.py

# Generate benchmarks
python "NetworkFlow/benchmark.py"

# Export appendix assets for LaTeX
python "NetworkFlow/export_appendix.py"

# Run on sample data
python -c "
from NetworkFlow.organ_transplant_flow import OrganTransplantNetworkFlow, generate_transplant_case

# Generate sample case
donors, recipients = generate_transplant_case(5, 5, seed=42)
solver = OrganTransplantNetworkFlow(donors, recipients)
max_flow, matches, iters = solver.ford_fulkerson_edmonds_karp()

print(f'Maximum successful transplants: {max_flow}')
print(f'Algorithm iterations: {iters}')
for donor_id, recipient_id in matches:
    print(f'  Donor {donor_id} → Recipient {recipient_id}')
"
```

## File Structure

```
NetworkFlow/
├── __init__.py                   # Module initialization
├── organ_transplant_flow.py      # Main algorithm implementation
├── benchmark.py                  # Performance benchmarking
├── export_appendix.py            # LaTeX appendix generation
├── validation.py                 # Correctness validation utilities
├── test_all.py                   # Comprehensive test suite
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── appendix/                     # Generated LaTeX files
│   ├── code_organ_transplant_flow.tex
│   ├── code_benchmark.tex
│   ├── figs.tex
│   └── tables.tex
├── figures/                      # Generated plots (PNG and PDF)
│   ├── runtime_vs_n.pdf
│   ├── runtime_vs_n.png
│   ├── transplants_vs_n.pdf
│   └── transplants_vs_n.png
└── results/                      # Generated CSV data
    ├── times.csv
    ├── transplants.csv
    ├── iterations.csv
    ├── compatibility.csv
    └── environment.txt
```

## LaTeX Integration

To include the appendix assets in your LaTeX document:

```latex
\input{NetworkFlow/appendix/code_organ_transplant_flow.tex}
\input{NetworkFlow/appendix/code_benchmark.tex}
\input{NetworkFlow/appendix/figs.tex}
\input{NetworkFlow/appendix/tables.tex}
```

## Algorithm Complexity

| Component | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Ford-Fulkerson (Edmonds-Karp) | O(VE²) | O(V + E) |
| Network Construction | O(nm) | O(nm) |
| Compatibility Check | O(1) per pair | O(1) |
| Overall | O(n³m²) | O(nm) |

Where:
- `n` = number of donors
- `m` = number of recipients
- `V = n + m + 2` (vertices: donors + recipients + source + sink)
- `E = n + nm + m` (edges: source→donors + donor↔recipient + recipients→sink)

## Example Usage

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from organ_transplant_flow import OrganTransplantNetworkFlow
from validation import validate_matching, analyze_network_structure

# Define donors: (num_organs, blood_type, tissue_markers)
donors = [
    (2, 'O', {'HLA-1', 'HLA-2', 'HLA-5'}),  # Universal donor, 2 organs
    (1, 'A', {'HLA-2', 'HLA-3', 'HLA-7'}),  # Type A, 1 organ
    (1, 'B', {'HLA-1', 'HLA-4', 'HLA-6'}),  # Type B, 1 organ
]

# Define recipients: (compatible_blood_types, tissue_markers, urgency)
recipients = [
    (['O', 'A'], {'HLA-1', 'HLA-2'}, 9),      # Type A, urgent
    (['O', 'B'], {'HLA-1', 'HLA-4'}, 7),      # Type B, moderate
    (['O'], {'HLA-5'}, 8),                     # Type O, urgent
]

# Solve
solver = OrganTransplantNetworkFlow(donors, recipients)
max_flow, matches, iterations = solver.ford_fulkerson_edmonds_karp()

print(f"Maximum transplants: {max_flow}")
print(f"Iterations: {iterations}")

# Validate solution
valid, msg = validate_matching(donors, recipients, matches, max_flow)
print(f"Valid: {valid} - {msg}")

# Analyze network structure
stats = analyze_network_structure(donors, recipients)
print(f"Compatible pairs: {stats['compatible_pairs']} / {len(donors) * len(recipients)}")
```

## Medical Compatibility Rules

### Blood Type Compatibility

| Donor Type | Can Donate To |
|------------|---------------|
| O | O, A, B, AB (Universal donor) |
| A | A, AB |
| B | B, AB |
| AB | AB only |

Equivalently, recipient compatibility:

| Recipient Type | Can Receive From |
|----------------|------------------|
| O | O only |
| A | O, A |
| B | O, B |
| AB | O, A, B, AB (Universal recipient) |

### Tissue Marker (HLA) Compatibility

- Requires at least 50% overlap between donor and recipient HLA markers
- Example: If recipient needs {HLA-1, HLA-2, HLA-3, HLA-4}, donor must have at least 2 of these markers
- Higher overlap reduces rejection risk in real transplants

## Testing

The test suite includes:
- Perfect matching scenarios
- Capacity constraint validation
- Blood type incompatibility cases
- Tissue marker incompatibility cases
- Empty case handling
- Random case validation (10+ seeds)
- Flow conservation verification
- Utility function testing

Run tests with: `python NetworkFlow/test_all.py`

### Test Coverage

| Test | Purpose |
|------|---------|
| `test_simple_perfect_match` | Basic correctness |
| `test_capacity_constraint` | Donor limits respected |
| `test_blood_incompatibility` | Blood type rules enforced |
| `test_tissue_incompatibility` | HLA matching enforced |
| `test_empty_case` | Edge case: no donors/recipients |
| `test_random_cases_validity` | Randomized testing (10 seeds) |
| `test_flow_conservation` | Each recipient matched once |
| `test_utility_functions` | Validation helpers work |

Expected output:
```
........
----------------------------------------------------------------------
Ran 9 tests in 0.XXX s

OK
```

## Validation Utilities

### `validation.py` provides:

1. **`validate_matching(donors, recipients, matches, max_flow)`**
   - Verifies flow value equals match count
   - Checks no recipient matched twice
   - Validates donor capacity constraints
   - Ensures medical compatibility
   - Returns: `(is_valid, error_message)`

2. **`count_compatible_pairs(donors, recipients)`**
   - Counts medically compatible donor-recipient pairs
   - Useful for understanding problem structure
   - Returns: `int` (number of compatible pairs)

3. **`analyze_network_structure(donors, recipients)`**
   - Analyzes network properties
   - Blood type distributions
   - Compatibility statistics
   - Returns: `dict` with statistics

Example:
```python
from validation import validate_matching, analyze_network_structure

# After solving...
valid, msg = validate_matching(donors, recipients, matches, max_flow)
assert valid, f"Invalid solution: {msg}"

stats = analyze_network_structure(donors, recipients)
print(f"Network has {stats['compatible_pairs']} compatible pairs")
print(f"Average compatibility: {stats['avg_compatibility']:.2%}")
```

## Benchmarking

The benchmarking suite measures:

1. **Runtime scaling**: Tests networks from 5 to 40 donors/recipients
2. **Transplant success rate**: Tracks how many recipients receive organs
3. **Algorithm iterations**: Counts augmenting paths found
4. **Compatibility patterns**: Analyzes different blood type distributions

Generated outputs:
- `runtime_vs_n.pdf`: Runtime vs network size with O(VE²) reference curve
- `transplants_vs_n.pdf`: Successful transplants vs network size
- `times.csv`: Detailed runtime measurements
- `transplants.csv`: Success rates per network size
- `iterations.csv`: Edmonds-Karp iteration counts
- `compatibility.csv`: Success rates under different blood type distributions

## Network Flow Construction

The algorithm constructs a flow network:

```
Source (s)
  ├─ capacity[a₁] ──> Donor 1
  ├─ capacity[a₂] ──> Donor 2
  └─ capacity[a₃] ──> Donor 3
                        │
                        ├─ capacity[1] ──> Recipient 1
                        ├─ capacity[1] ──> Recipient 2  ──> Sink (t)
                        └─ capacity[1] ──> Recipient 3
```

Where:
- Source edges have capacity = donor's available organs
- Donor-recipient edges exist only if medically compatible, capacity = 1
- Recipient-sink edges have capacity = 1 (each needs one organ)

Maximum flow = maximum number of successful transplants.

## Proof of Correctness

The reduction to maximum flow is correct because:

1. **Flow ⟹ Matching**: Any feasible flow corresponds to a valid matching
   - Integer capacities guarantee integer flow (integrality theorem)
   - Flow on edge (donor, recipient) indicates assignment
   - Source edge capacities enforce donor limits
   - Sink edge capacities enforce one organ per recipient

2. **Matching ⟹ Flow**: Any valid matching can be realized as a flow
   - Send flow along source → donor → recipient → sink paths
   - Flow value equals number of matches
   - All capacity constraints satisfied by construction

3. **Optimality**: Ford-Fulkerson finds maximum flow, which equals maximum matching

## Real-World Applications

This algorithm models real organ allocation systems like:
- **UNOS** (United Network for Organ Sharing) in the United States
- **Eurotransplant** in Europe
- **National registries** worldwide

Extensions in practice include:
- Geographic distance constraints
- Waiting time priority scores
- Multi-organ transplants
- Paired kidney donations (kidney exchange chains)
- Dynamic arrival of donors and recipients

## Workflow

```
1. Write Python code (organ_transplant_flow.py)
   ↓
2. Run tests (test_all.py) → verify correctness
   ↓
3. Run benchmarks (benchmark.py) → generate figures/ and results/
   ↓
4. Export appendix (export_appendix.py) → generate appendix/ LaTeX files
   ↓
5. Compile LaTeX → includes generated appendix files
```

## References

- Ford, L. R., & Fulkerson, D. R. (1956). Maximal flow through a network. *Canadian Journal of Mathematics*, 8, 399-404.
- Edmonds, J., & Karp, R. M. (1972). Theoretical improvements in algorithmic efficiency for network flow problems. *Journal of the ACM*, 19(2), 248-264.
- Bertsimas, D., Farias, V. F., & Trichakis, N. (2013). Fairness, efficiency, and flexibility in organ allocation for kidney transplantation. *Operations Research*, 61(1), 73-87.
