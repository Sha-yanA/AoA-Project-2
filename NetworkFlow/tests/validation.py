"""Validation utilities for organ transplant network flow."""

from __future__ import annotations

from typing import List, Tuple, Set


def validate_matching(
    donors: List[Tuple[int, str, Set[str]]],
    recipients: List[Tuple[List[str], Set[str], int]],
    matches: List[Tuple[int, int]],
    max_flow: int
) -> Tuple[bool, str]:
    """
    Validate that a matching is correct.
    
    Checks:
    1. Flow value equals number of matches
    2. No recipient matched more than once
    3. Donor capacity constraints respected
    4. All matches are medically compatible
    
    Args:
        donors: List of (num_organs, blood_type, tissue_markers)
        recipients: List of (compatible_blood_types, tissue_markers, urgency)
        matches: List of (donor_id, recipient_id) pairs
        max_flow: Claimed maximum flow value
    
    Returns:
        (is_valid, error_message)
    """
    # Check 1: Flow equals matches
    if max_flow != len(matches):
        return False, f"Flow value {max_flow} doesn't match number of matches {len(matches)}"
    
    # Check 2: No recipient matched twice
    recipient_used = set()
    for _, recipient_id in matches:
        if recipient_id in recipient_used:
            return False, f"Recipient {recipient_id} matched multiple times"
        recipient_used.add(recipient_id)
    
    # Check 3: Donor capacity constraints
    donor_usage = {}
    for donor_id, _ in matches:
        donor_usage[donor_id] = donor_usage.get(donor_id, 0) + 1
    
    for donor_id, count in donor_usage.items():
        num_organs, _, _ = donors[donor_id]
        if count > num_organs:
            return False, f"Donor {donor_id} exceeds capacity: {count} > {num_organs}"
    
    # Check 4: Medical compatibility
    for donor_id, recipient_id in matches:
        _, d_blood, d_tissue = donors[donor_id]
        r_blood_compat, r_tissue, _ = recipients[recipient_id]
        
        # Blood compatibility
        if d_blood not in r_blood_compat:
            return False, f"Blood incompatible: Donor {donor_id} ({d_blood}) → Recipient {recipient_id} (needs {r_blood_compat})"
        
        # Tissue compatibility (50% match required)
        if len(r_tissue) > 0:
            match_count = len(d_tissue & r_tissue)
            if match_count < len(r_tissue) * 0.5:
                return False, f"Tissue incompatible: Donor {donor_id} → Recipient {recipient_id} (only {match_count}/{len(r_tissue)} markers match)"
    
    return True, "Valid matching"


def count_compatible_pairs(
    donors: List[Tuple[int, str, Set[str]]],
    recipients: List[Tuple[List[str], Set[str], int]]
) -> int:
    """
    Count number of compatible donor-recipient pairs.
    
    Useful for understanding the problem structure.
    """
    count = 0
    for i, (_, d_blood, d_tissue) in enumerate(donors):
        for j, (r_blood_compat, r_tissue, _) in enumerate(recipients):
            # Blood check
            if d_blood not in r_blood_compat:
                continue
            
            # Tissue check
            if len(r_tissue) > 0:
                match_count = len(d_tissue & r_tissue)
                if match_count < len(r_tissue) * 0.5:
                    continue
            
            count += 1
    
    return count


def analyze_network_structure(
    donors: List[Tuple[int, str, Set[str]]],
    recipients: List[Tuple[List[str], Set[str], int]]
) -> dict:
    """
    Analyze the structure of the transplant network.
    
    Returns statistics about the problem instance.
    """
    total_organs = sum(num for num, _, _ in donors)
    total_recipients = len(recipients)
    compatible_pairs = count_compatible_pairs(donors, recipients)
    
    # Blood type distribution
    blood_types_donors = {}
    for _, blood, _ in donors:
        blood_types_donors[blood] = blood_types_donors.get(blood, 0) + 1
    
    blood_types_recipients = {}
    for blood_compat, _, _ in recipients:
        # Take most restrictive blood type for counting
        if 'O' in blood_compat and len(blood_compat) == 1:
            key = 'O'
        elif 'AB' in blood_compat and len(blood_compat) == 4:
            key = 'AB'
        elif 'A' in blood_compat and 'B' not in blood_compat:
            key = 'A'
        elif 'B' in blood_compat and 'A' not in blood_compat:
            key = 'B'
        else:
            key = 'other'
        blood_types_recipients[key] = blood_types_recipients.get(key, 0) + 1
    
    return {
        'n_donors': len(donors),
        'n_recipients': len(recipients),
        'total_organs': total_organs,
        'compatible_pairs': compatible_pairs,
        'avg_compatibility': compatible_pairs / (len(donors) * len(recipients)) if donors and recipients else 0,
        'blood_types_donors': blood_types_donors,
        'blood_types_recipients': blood_types_recipients,
    }


__all__ = [
    "validate_matching",
    "count_compatible_pairs",
    "analyze_network_structure",
]