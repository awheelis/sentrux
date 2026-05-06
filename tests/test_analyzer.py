"""Tests for project analyzer."""

import tempfile
from pathlib import Path

import pytest

from sentrux.core.analyzer import ProjectAnalyzer


def test_analyze_simple_project():
    """Test analyzing a simple project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test files
        (tmpdir / "main.py").write_text("""
def main():
    return "hello"
""")

        (tmpdir / "utils.py").write_text("""
import main

def helper():
    return main.main()
""")

        analyzer = ProjectAnalyzer(tmpdir)
        result = analyzer.analyze()

        assert result.project_path == str(tmpdir)
        assert len(result.files) == 2
        assert result.quality_score is not None
        assert 0 <= result.quality_score.overall_score <= 10000
        assert 0 <= result.quality_score.modularity <= 1
        assert 0 <= result.quality_score.acyclicity <= 1


def test_quality_score_calculation():
    """Test quality score is calculated correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        (tmpdir / "module.py").write_text("""
def func1():
    pass

def func2():
    pass

class MyClass:
    def method(self):
        pass
""")

        analyzer = ProjectAnalyzer(tmpdir)
        result = analyzer.analyze()

        assert result.quality_score is not None
        # All metrics should be calculated
        assert hasattr(result.quality_score, "modularity")
        assert hasattr(result.quality_score, "acyclicity")
        assert hasattr(result.quality_score, "depth")
        assert hasattr(result.quality_score, "equality")
        assert hasattr(result.quality_score, "redundancy")
