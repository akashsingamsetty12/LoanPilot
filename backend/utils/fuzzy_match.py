"""
Fuzzy String Matching
======================
RapidFuzz-based string comparison utilities for name, address,
and organization matching in cross-document verification.


GOLDEN RULE: Use RapidFuzz ONLY for string variations (e.g. "Jon Smith" vs "John Smith").
Hard facts (numbers, dates) use deterministic exact comparison.
"""

from rapidfuzz import fuzz


def names_match(name1: str, name2: str, threshold: int = 85) -> tuple[bool, float]:
    """
    Compare two person names using token_sort_ratio (order-insensitive).

    Args:
        name1: First name string
        name2: Second name string
        threshold: Minimum score to consider a match (0–100)

    Returns:
        (is_match, score) — e.g. (True, 92.5)

    Example:
        names_match("Rahul Kumar", "Kumar Rahul") → (True, 100.0)
        names_match("Jon Smith", "John Smith")    → (True, 88.9)
    """
    # TODO: Implement name matching logic
    score = fuzz.token_sort_ratio(name1.strip().lower(), name2.strip().lower())
    return score >= threshold, score


def addresses_match(addr1: str, addr2: str, threshold: int = 80) -> tuple[bool, float]:
    """
    Compare two addresses using partial_ratio (handles abbreviations).

    Returns:
        (is_match, score)
    """
    # TODO: Implement address matching logic
    score = fuzz.partial_ratio(addr1.strip().lower(), addr2.strip().lower())
    return score >= threshold, score


def organizations_match(org1: str, org2: str, threshold: int = 85) -> tuple[bool, float]:
    """
    Compare two organization/employer names.

    Example:
        organizations_match("Horizon Tech Pvt Ltd", "Horizon Tech") → (True, 87.0)
    """
    # TODO: Implement organization matching logic
    score = fuzz.token_sort_ratio(org1.strip().lower(), org2.strip().lower())
    return score >= threshold, score
