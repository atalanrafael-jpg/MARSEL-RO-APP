"""Regression test for the canonical GitHub repository identity."""

import os

from scripts import marsel_canonical_self_check as check


def test_expected_repository_matches_actual_github_repository_name():
    """The canonical identity must match GitHub's actual full_name exactly."""
    actual_repository = "atalanrafael-jpg/MARSEL-ro-app"
    assert check.EXPECTED_REPOSITORY == actual_repository
