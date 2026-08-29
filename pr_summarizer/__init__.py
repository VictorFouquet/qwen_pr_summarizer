"""Grounded PR summarizer with a reference-free faithfulness guard."""

from .verifier import Claim, ClaimKind, Verification, extract_claims, verify

__all__ = ["Claim", "ClaimKind", "Verification", "extract_claims", "verify"]
