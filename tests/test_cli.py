"""Tests for the CLI."""

import subprocess
import sys
from pathlib import Path


def test_help_flag():
    """Test that --help flag works and exits cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "psychoanalyze", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "psychoanalyze" in result.stdout
    assert "usage" in result.stdout.lower() or "psychoanalyze" in result.stdout


def test_version_flag():
    """Test that --version flag outputs the version string."""
    result = subprocess.run(
        [sys.executable, "-m", "psychoanalyze", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Version is normalized by setuptools from 1.0.0-alpha.1 to 1.0.0a1
    assert "1.0.0a1" in result.stdout
