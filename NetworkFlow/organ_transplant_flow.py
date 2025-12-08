"""Organ transplant network flow matching algorithm."""

from __future__ import annotations

from collections import deque, defaultdict
from typing import List, Tuple, Set
import random


class OrganTransplantNetworkFlow:
    """
    Network flow solution for organ transplant matching.
    
    Models donor-recipient matching with medical compatibility constraints
    (blood type, tissue markers) as a maximum flow problem.
    """
    
    def __init__(
        self,
        donors: List[Tuple[int, str, Set[str]]],
        recipients: List[Tuple[List[str], Set[str], int]]
    ):
        """
        Initialize transplant network.
        
        Args:
            donors: List of (num_organs, blood_type, tissue_markers)
            recipients: List of (compatible_blood_types, tissue_markers, urgency)
        """
        self.donors = donors
        self.recipients = recipients
        self.n_donors = len(donors)
        self.n_recipients = len(recipients)
        
        # Node indexing: 0=source, 1..n_donors=donors,
        # n_donors+1..n_donors+n_recipients=recipients, last=sink
        self.source = 0
        self.sink = self.n_donors + self.n_recipients + 1
        self.total_nodes = self.n_donors + self.n_recipients + 2
        
        # Build flow network
        self.graph = defaultdict(dict)
        self._build_network()
    
    def _check_compatibility(
        self,
        donor_blood: str,
        donor_tissue: Set[str],
        recip_blood_compat: List[str],
        recip_tissue: Set[str]
    ) -> bool:
        """
        Check medical compatibility between donor and recipient.
        
        Blood type compatibility:
        - O can donate to anyone
        - A can donate to A, AB
        - B can donate to B, AB
        - AB can donate to AB only
        
        Tissue compatibility: at least 50% marker match required
        """
        # Blood type check
        blood_compatible = donor_blood in recip_blood_compat
        
        # Tissue marker check
        if len(donor_tissue) == 0 or len(recip_tissue) == 0:
            tissue_compatible = True
        else:
            match_count = len(donor_tissue & recip_tissue)
            tissue_compatible = match_count >= len(recip_tissue) * 0.5
        
        return blood_compatible and tissue_compatible
    
    def _build_network(self) -> None:
        """Construct flow network from transplant matching problem."""
        # Source to donors (capacity = available organs)
        for i, (num_organs, blood_type, tissue) in enumerate(self.donors):
            donor_node = i + 1
            self.graph[self.source][donor_node] = num_organs
        
        # Donors to recipients (if compatible)
        for i, (num_organs, d_blood, d_tissue) in enumerate(self.donors):
            donor_node = i + 1
            for j, (r_blood_compat, r_tissue, urgency) in enumerate(self.recipients):
                recipient_node = self.n_donors + j + 1
                if self._check_compatibility(d_blood, d_tissue, r_blood_compat, r_tissue):
                    self.graph[donor_node][recipient_node] = 1  # One organ per match
        
        # Recipients to sink (capacity = 1, each needs one organ)
        for j, (r_blood, r_tissue, urgency) in enumerate(self.recipients):
            recipient_node = self.n_donors + j + 1
            self.graph[recipient_node][self.sink] = 1
    
    def bfs(self, residual_graph: dict, parent: dict) -> bool:
        """
        Breadth-First Search to find augmenting path.
        
        Returns:
            True if path exists from source to sink
        """
        visited = set([self.source])
        queue = deque([self.source])
        
        while queue:
            u = queue.popleft()
            
            for v in residual_graph.get(u, {}):
                if v not in visited and residual_graph[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    if v == self.sink:
                        return True
                    queue.append(v)
        
        return False
    
    def ford_fulkerson_edmonds_karp(self) -> Tuple[int, List[Tuple[int, int]], int]:
        """
        Ford-Fulkerson algorithm using Edmonds-Karp (BFS for paths).
        
        Time Complexity: O(VE^2) where V = nodes, E = edges
        
        Returns:
            (max_flow_value, matching_list, iterations)
        """
        # Create residual graph
        residual = defaultdict(dict)
        for u in self.graph:
            for v in self.graph[u]:
                residual[u][v] = self.graph[u][v]
                if v not in residual:
                    residual[v] = {}
                if u not in residual[v]:
                    residual[v][u] = 0
        
        parent = {}
        max_flow = 0
        iterations = 0
        
        # Find augmenting paths
        while self.bfs(residual, parent):
            iterations += 1
            
            # Find bottleneck capacity
            path_flow = float('inf')
            v = self.sink
            while v != self.source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                v = u
            
            # Update residual capacities
            v = self.sink
            while v != self.source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = u
            
            max_flow += path_flow
            parent = {}
        
        # Extract matching
        matches = []
        for i in range(self.n_donors):
            donor_node = i + 1
            for j in range(self.n_recipients):
                recipient_node = self.n_donors + j + 1
                if recipient_node in self.graph.get(donor_node, {}):
                    original_cap = self.graph[donor_node][recipient_node]
                    residual_cap = residual.get(donor_node, {}).get(recipient_node, 0)
                    flow = original_cap - residual_cap
                    if flow > 0:
                        matches.append((i, j))
        
        return max_flow, matches, iterations


def generate_transplant_case(
    n_donors: int,
    n_recipients: int,
    seed: int | None = None
) -> Tuple[List, List]:
    """
    Generate random transplant case with realistic distributions.
    
    Args:
        n_donors: Number of donors
        n_recipients: Number of recipients
        seed: Random seed for reproducibility
    
    Returns:
        (donors_list, recipients_list)
    """
    if n_donors < 0 or n_recipients < 0:
        raise ValueError("Counts must be non-negative")
    
    prng = random.Random(seed)
    
    # Realistic blood type distributions
    blood_types = ['O', 'A', 'B', 'AB']
    blood_weights = [0.45, 0.40, 0.11, 0.04]
    
    # HLA tissue markers
    all_markers = [f"HLA-{i}" for i in range(10)]
    
    # Generate donors
    donors = []
    for _ in range(n_donors):
        num_organs = prng.choices([1, 2], weights=[0.8, 0.2])[0]
        blood = prng.choices(blood_types, weights=blood_weights)[0]
        tissue = set(prng.sample(all_markers, prng.randint(3, 6)))
        donors.append((num_organs, blood, tissue))
    
    # Generate recipients
    recipients = []
    for _ in range(n_recipients):
        recipient_blood = prng.choices(blood_types, weights=blood_weights)[0]
        
        # Determine compatible blood types
        if recipient_blood == 'O':
            blood_compatible = ['O']
        elif recipient_blood == 'A':
            blood_compatible = ['O', 'A']
        elif recipient_blood == 'B':
            blood_compatible = ['O', 'B']
        else:  # AB
            blood_compatible = blood_types
        
        tissue = set(prng.sample(all_markers, prng.randint(3, 5)))
        urgency = prng.randint(1, 10)
        recipients.append((blood_compatible, tissue, urgency))
    
    return donors, recipients


__all__ = [
    "OrganTransplantNetworkFlow",
    "generate_transplant_case",
]