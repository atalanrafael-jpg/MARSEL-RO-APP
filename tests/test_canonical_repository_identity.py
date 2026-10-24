"""Regression tests for canonical GitHub repository identity."""

from scripts import marsel_canonical_self_check as check


def test_repository_identity_accepts_github_case_variation():
    """GitHub repository names are case-insensitive identifiers."""
    assert check.repository_names_match(
        "atalanrafael-jpg/MARSEL-ro-app",
        "atalanrafael-jpg/MARSEL-Ro-app",
    )


def test_repository_identity_rejects_a_different_repository():
    """Case-insensitive matching must not accept another repository."""
    assert not check.repository_names_match(
        "another-owner/MARSEL-ro-app",
        "atalanrafael-jpg/MARSEL-Ro-app",
    )
