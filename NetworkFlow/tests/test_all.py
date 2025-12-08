"""Test suite for organ transplant network flow."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from organ_transplant_flow import OrganTransplantNetworkFlow, generate_transplant_case
from validation import validate_matching, count_compatible_pairs, analyze_network_structure


class TestOrganTransplantFlow(unittest.TestCase):
    """Test cases for organ transplant matching."""
    
    def test_simple_perfect_match(self):
        """Test case with perfect one-to-one matching."""
        # 2 donors, 2 recipients, perfect compatibility
        donors = [
            (1, 'O', {'HLA-1', 'HLA-2'}),  # Universal donor
            (1, 'A', {'HLA-3', 'HLA-4'}),
        ]
        recipients = [
            (['O', 'A', 'B', 'AB'], {'HLA-1'}, 5),  # Can receive from anyone
            (['O', 'A'], {'HLA-3'}, 8),
        ]
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        self.assertEqual(max_flow, 2, "Should match both recipients")
        valid, msg = validate_matching(donors, recipients, matches, max_flow)
        self.assertTrue(valid, msg)
    
    def test_capacity_constraint(self):
        """Test that donor capacity limits are respected."""
        # 1 donor with 2 organs, 3 recipients
        donors = [
            (2, 'O', {'HLA-1', 'HLA-2', 'HLA-3'}),
        ]
        recipients = [
            (['O'], {'HLA-1'}, 9),
            (['O'], {'HLA-2'}, 8),
            (['O'], {'HLA-3'}, 7),
        ]
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        self.assertLessEqual(max_flow, 2, "Cannot exceed donor capacity of 2")
        valid, msg = validate_matching(donors, recipients, matches, max_flow)
        self.assertTrue(valid, msg)
    
    def test_blood_incompatibility(self):
        """Test that blood type constraints are enforced."""
        # Type AB donor, Type O recipient (incompatible)
        donors = [
            (1, 'AB', {'HLA-1', 'HLA-2'}),
        ]
        recipients = [
            (['O'], {'HLA-1'}, 10),  # Type O can only receive from O
        ]
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        self.assertEqual(max_flow, 0, "Should have no matches due to blood incompatibility")
    
    def test_tissue_incompatibility(self):
        """Test that tissue marker constraints are enforced."""
        # Compatible blood type but poor tissue match
        donors = [
            (1, 'O', {'HLA-1', 'HLA-2'}),
        ]
        recipients = [
            (['O'], {'HLA-5', 'HLA-6', 'HLA-7', 'HLA-8'}, 10),  # 0% match
        ]
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        self.assertEqual(max_flow, 0, "Should have no matches due to tissue incompatibility")
    
    def test_empty_case(self):
        """Test with no donors or recipients."""
        donors = []
        recipients = []
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        self.assertEqual(max_flow, 0)
        self.assertEqual(len(matches), 0)
    
    def test_random_cases_validity(self):
        """Test randomly generated cases for correctness."""
        for seed in range(10):
            with self.subTest(seed=seed):
                donors, recipients = generate_transplant_case(5, 5, seed=seed)
                solver = OrganTransplantNetworkFlow(donors, recipients)
                max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
                
                valid, msg = validate_matching(donors, recipients, matches, max_flow)
                self.assertTrue(valid, f"Seed {seed}: {msg}")
    
    def test_flow_conservation(self):
        """Test that flow is conserved at intermediate nodes."""
        donors = [
            (2, 'O', {'HLA-1', 'HLA-2'}),
            (1, 'A', {'HLA-3'}),
        ]
        recipients = [
            (['O', 'A'], {'HLA-1'}, 9),
            (['O'], {'HLA-2'}, 8),
        ]
        
        solver = OrganTransplantNetworkFlow(donors, recipients)
        max_flow, matches, _ = solver.ford_fulkerson_edmonds_karp()
        
        # Check that each recipient matched at most once
        recipient_matches = {}
        for _, recipient_id in matches:
            recipient_matches[recipient_id] = recipient_matches.get(recipient_id, 0) + 1
        
        for recipient_id, count in recipient_matches.items():
            self.assertEqual(count, 1, f"Recipient {recipient_id} matched {count} times")
    
    def test_utility_functions(self):
        """Test validation and analysis utilities."""
        donors = [(1, 'O', {'HLA-1'})]
        recipients = [(['O'], {'HLA-1'}, 5)]
        
        # Test compatibility counting
        count = count_compatible_pairs(donors, recipients)
        self.assertEqual(count, 1)
        
        # Test network analysis
        analysis = analyze_network_structure(donors, recipients)
        self.assertEqual(analysis['n_donors'], 1)
        self.assertEqual(analysis['n_recipients'], 1)
        self.assertEqual(analysis['total_organs'], 1)


if __name__ == "__main__":
    unittest.main()