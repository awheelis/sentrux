"""Tests for Python parser."""

import tempfile
from pathlib import Path


from sentrux.core.parser import PythonParser, ProjectParser


def test_parse_simple_file():
    """Test parsing a simple Python file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
def hello():
    return "world"

class MyClass:
    pass

import os
from pathlib import Path
""")
        f.flush()

        analysis = PythonParser.parse_file(Path(f.name))

        assert analysis.functions == ["hello"]
        assert analysis.classes == ["MyClass"]
        assert "os" in analysis.imports
        assert "pathlib" in analysis.imports
        assert analysis.line_count > 0
        assert analysis.cyclomatic_complexity >= 1


def test_parse_project():
    """Test parsing a project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test files
        (tmpdir / "module1.py").write_text("""
def func1():
    pass
""")

        (tmpdir / "module2.py").write_text("""
import module1

def func2():
    return module1.func1()
""")

        files = ProjectParser.parse_project(tmpdir)

        assert len(files) == 2
        assert "module1.py" in files
        assert "module2.py" in files
        assert files["module1.py"].functions == ["func1"]
        assert files["module2.py"].functions == ["func2"]


def test_cyclomatic_complexity():
    """Test cyclomatic complexity calculation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
def complex_func(x):
    if x > 0:
        return x
    elif x < 0:
        return -x
    else:
        return 0
""")
        f.flush()

        analysis = PythonParser.parse_file(Path(f.name))

        # Base complexity 1 + 1 for if + 1 for elif = 3
        assert analysis.cyclomatic_complexity >= 3
