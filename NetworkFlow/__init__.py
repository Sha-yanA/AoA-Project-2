"""Protein interaction network vertex cover utilities."""

from .protein_network import (
    ProteinInteractionNetwork,
    generate_scale_free_ppi,
)

__all__ = [
    "ProteinInteractionNetwork",
    "generate_scale_free_ppi",
]
