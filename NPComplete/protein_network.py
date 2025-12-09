"""Protein interaction networks cast as a vertex cover problem for drug targeting.

Proteins correspond to vertices and pairwise interactions correspond to undirected
edges; a vertex cover is a minimal drug-target set that disrupts every interaction.
Algorithms provided: edge-based greedy 2-approximation (O(V + E)), degree-based
greedy heuristic (O(V^2 + E)), and a brute-force exact solver (O(2^n · poly(n)))
for small instances. Includes a Barabási–Albert generator with a deterministic
fallback when networkx is unavailable.
"""

from __future__ import annotations

import random
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple


class ProteinInteractionNetwork:
    """Undirected simple graph representing a protein–protein interaction network.

    Proteins ↔ vertices, interactions ↔ edges; a vertex cover is a set of proteins
    whose inhibition touches every interaction (minimal drug-target set).
    """

    def __init__(self, proteins: List[str], interactions: List[Tuple[str, str]]) -> None:
        """Initialize the network with validation.

        Ensures endpoints exist, forbids self-loops, and ignores duplicate edges.
        Adjacency is stored as a mapping from protein to a set of neighboring proteins.
        """

        self._vertices: Set[str] = set(proteins)
        if not self._vertices and interactions:
            raise ValueError("Cannot add interactions without proteins.")

        self._adjacency: Dict[str, Set[str]] = {p: set() for p in self._vertices}
        for u, v in interactions:
            if u == v:
                raise ValueError(f"Self-loop detected on {u}.")
            if u not in self._vertices or v not in self._vertices:
                raise ValueError(f"Interaction ({u}, {v}) references unknown protein(s).")
            if v in self._adjacency[u]:
                continue  # ignore duplicates
            self._adjacency[u].add(v)
            self._adjacency[v].add(u)

    @staticmethod
    def from_barabasi_albert(
        n: int, m: int, seed: int = 42, prefix: str = "P"
    ) -> "ProteinInteractionNetwork":
        """Generate a preferential-attachment PPI network.

        Prefers networkx.barabasi_albert_graph; otherwise uses a deterministic
        degree-proportional fallback. Node labels are f"{prefix}{i}".
        """

        if n <= 0 or m <= 0:
            raise ValueError("n and m must be positive integers.")

        try:
            import networkx as nx  # type: ignore

            g = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
            proteins = [f"{prefix}{i}" for i in range(n)]
            edges = [(proteins[u], proteins[v]) for u, v in g.edges()]
            return ProteinInteractionNetwork(proteins, edges)
        except Exception:
            return ProteinInteractionNetwork._fallback_barabasi_albert(n, m, seed, prefix)

    @staticmethod
    def _fallback_barabasi_albert(
        n: int, m: int, seed: int, prefix: str
    ) -> "ProteinInteractionNetwork":
        """Deterministic preferential-attachment generator without networkx.

        Starts from a clique on min(n, m + 1) nodes, then adds nodes one by one,
        connecting each new node to m existing nodes sampled with probability
        proportional to degree (implemented via the repeated-nodes list trick).
        """

        rng = random.Random(seed)
        node_count = n
        base = min(n, max(2, m + 1))
        edges: Set[Tuple[int, int]] = set()

        # Start with a clique on "base" nodes.
        for i in range(base):
            for j in range(i + 1, base):
                edges.add((i, j))

        repeated_nodes: List[int] = []
        for i in range(base):
            # In a clique of size base, degree is base-1.
            repeated_nodes.extend([i] * (base - 1))

        # Attach remaining nodes preferentially.
        for new_node in range(base, node_count):
            targets: Set[int] = set()
            while len(targets) < m and repeated_nodes:
                targets.add(rng.choice(repeated_nodes))
            if not targets:
                targets = set(rng.sample(range(new_node), k=min(m, new_node)))
            for t in targets:
                u, v = sorted((new_node, t))
                edges.add((u, v))
            repeated_nodes.extend(targets)
            repeated_nodes.extend([new_node] * max(len(targets), m))

        proteins = [f"{prefix}{i}" for i in range(node_count)]
        labeled_edges = [(proteins[u], proteins[v]) for u, v in edges]
        return ProteinInteractionNetwork(proteins, labeled_edges)

    def vertices(self) -> List[str]:
        """Return proteins in deterministic sorted order."""

        return sorted(self._vertices)

    def edges(self) -> List[Tuple[str, str]]:
        """Return edges as sorted pairs in deterministic order."""

        edge_list: List[Tuple[str, str]] = []
        for u in self.vertices():
            for v in sorted(self._adjacency[u]):
                if u < v:
                    edge_list.append((u, v))
        return edge_list

    def stats(self) -> Dict[str, float]:
        """Compute basic graph statistics."""

        n = len(self._vertices)
        m = sum(len(neigh) for neigh in self._adjacency.values()) // 2
        density = 0.0 if n <= 1 else 2.0 * m / (n * (n - 1))
        degrees = [len(neigh) for neigh in self._adjacency.values()]
        max_degree = max(degrees) if degrees else 0
        avg_degree = 0.0 if n == 0 else sum(degrees) / n
        return {
            "n": n,
            "m": m,
            "density": density,
            "max_degree": max_degree,
            "avg_degree": avg_degree,
        }

    def is_vertex_cover(self, cover: Set[str]) -> bool:
        """Return True iff every interaction has an endpoint in cover."""

        for u in self._vertices:
            for v in self._adjacency[u]:
                if u < v and u not in cover and v not in cover:
                    return False
        return True

    def greedy_vertex_cover_edge_based(self, seed: int = 42) -> Set[str]:
        """Edge-based 2-approximation in O(V + E) time.

        Repeatedly select an uncovered edge (deterministic randomness via seed),
        add both endpoints to the cover, and remove all incident uncovered edges.
        """

        rng = random.Random(seed)
        cover: Set[str] = set()
        edges = self.edges()
        vertex_to_edges: Dict[str, Set[int]] = {v: set() for v in self._vertices}
        for idx, (u, v) in enumerate(edges):
            vertex_to_edges[u].add(idx)
            vertex_to_edges[v].add(idx)

        active: List[int] = list(range(len(edges)))
        positions: Dict[int, int] = {idx: idx for idx in active}

        def remove_edge_idx(idx: int) -> None:
            pos = positions.pop(idx, None)
            if pos is None:
                return
            last = active.pop()
            if pos < len(active):
                active[pos] = last
                positions[last] = pos

        while active:
            idx = rng.choice(active)
            u, v = edges[idx]
            cover.update((u, v))
            for vertex in (u, v):
                incident = list(vertex_to_edges[vertex])
                for e_idx in incident:
                    remove_edge_idx(e_idx)
                    other = edges[e_idx][0] if edges[e_idx][1] == vertex else edges[e_idx][1]
                    vertex_to_edges[other].discard(e_idx)
                vertex_to_edges[vertex].clear()
        return cover

    def greedy_vertex_cover_degree_based(self) -> Set[str]:
        """Degree-based greedy heuristic in O(V^2 + E) time.

        Each iteration selects a current maximum-degree protein (lexicographically
        smallest among ties), adds it to the cover, and deletes incident edges.
        """

        remaining: Dict[str, Set[str]] = {v: set(neigh) for v, neigh in self._adjacency.items()}
        cover: Set[str] = set()

        while True:
            degrees = {v: len(neigh) for v, neigh in remaining.items()}
            if not degrees:
                break
            max_degree = max(degrees.values()) if degrees else 0
            if max_degree == 0:
                break
            candidates = [v for v, deg in degrees.items() if deg == max_degree]
            chosen = min(candidates)
            cover.add(chosen)
            for nbr in list(remaining[chosen]):
                remaining[nbr].discard(chosen)
            remaining[chosen].clear()
        return cover

    def brute_force_optimal_vertex_cover(self, max_n: int = 18) -> Optional[Set[str]]:
        """Exact minimum vertex cover by size-ordered enumeration.

        Returns None when the instance exceeds max_n to avoid exponential work.
        Otherwise enumerates subsets by increasing size and returns the first cover.
        """

        vertices = self.vertices()
        if len(vertices) > max_n:
            return None
        edge_list = self.edges()
        for k in range(len(vertices) + 1):
            for subset in combinations(vertices, k):
                candidate = set(subset)
                if self._covers_all_edges(candidate, edge_list):
                    return candidate
        return set()

    @staticmethod
    def _covers_all_edges(cover: Set[str], edges: List[Tuple[str, str]]) -> bool:
        return all(u in cover or v in cover for u, v in edges)


if __name__ == "__main__":
    proteins = ["P1", "P2", "P3", "P4", "P5"]
    interactions = [("P1", "P2"), ("P2", "P3"), ("P3", "P4"), ("P4", "P5"), ("P1", "P5")]
    net = ProteinInteractionNetwork(proteins, interactions)

    print("Vertices:", net.vertices())
    print("Edges:", net.edges())
    print("Stats:", net.stats())

    edge_cover = net.greedy_vertex_cover_edge_based(seed=123)
    degree_cover = net.greedy_vertex_cover_degree_based()
    optimal_cover = net.brute_force_optimal_vertex_cover(max_n=10)

    print("Edge-based cover:", edge_cover)
    print("Degree-based cover:", degree_cover)
    print("Optimal cover:", optimal_cover)

    assert net.is_vertex_cover(edge_cover)
    assert net.is_vertex_cover(degree_cover)
    if optimal_cover is not None:
        assert net.is_vertex_cover(optimal_cover)
