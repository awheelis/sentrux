"""Python AST parser for extracting code structure."""

import ast
from pathlib import Path
from typing import Dict, List, Set

from sentrux.models.analysis import FileAnalysis


class PythonParser:
    """Parse Python files and extract structure using AST."""

    @staticmethod
    def parse_file(file_path: Path) -> FileAnalysis:
        """Parse a Python file and extract structure."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            return FileAnalysis(path=str(file_path), module_name="")

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return FileAnalysis(path=str(file_path), module_name="")

        module_name = PythonParser._module_name_from_path(file_path)
        functions = PythonParser._extract_functions(tree)
        classes = PythonParser._extract_classes(tree)
        imports = PythonParser._extract_imports(tree)
        complexity = PythonParser._calculate_cyclomatic_complexity(tree)
        line_count = len(content.split("\n"))

        return FileAnalysis(
            path=str(file_path),
            module_name=module_name,
            functions=functions,
            classes=classes,
            imports=imports,
            cyclomatic_complexity=complexity,
            line_count=line_count,
        )

    @staticmethod
    def _module_name_from_path(file_path: Path) -> str:
        """Convert file path to module name."""
        if file_path.name == "__init__.py":
            return str(file_path.parent.name)
        return file_path.stem

    @staticmethod
    def _extract_functions(tree: ast.AST) -> List[str]:
        """Extract all function names from AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        return functions

    @staticmethod
    def _extract_classes(tree: ast.AST) -> List[str]:
        """Extract all class names from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return classes

    @staticmethod
    def _extract_imports(tree: ast.AST) -> List[str]:
        """Extract all imported modules."""
        imports: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return sorted(list(imports))

    @staticmethod
    def _calculate_cyclomatic_complexity(tree: ast.AST) -> float:
        """Calculate cyclomatic complexity of the module."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return float(complexity)


class ProjectParser:
    """Parse all Python files in a project."""

    @staticmethod
    def parse_project(project_path: Path) -> Dict[str, FileAnalysis]:
        """Parse all Python files in a project."""
        files: Dict[str, FileAnalysis] = {}
        python_files = ProjectParser._find_python_files(project_path)

        for file_path in python_files:
            analysis = PythonParser.parse_file(file_path)
            files[str(file_path.relative_to(project_path))] = analysis

        return files

    @staticmethod
    def _find_python_files(project_path: Path, max_depth: int = 10) -> List[Path]:
        """Find all Python files in project, respecting .gitignore."""
        python_files = []
        excluded_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            ".pytest_cache",
            ".tox",
            "build",
            "dist",
            "*.egg-info",
            "node_modules",
        }

        def _walk(path: Path, depth: int = 0) -> None:
            if depth > max_depth:
                return

            try:
                for item in path.iterdir():
                    if item.is_dir():
                        if item.name in excluded_dirs or item.name.startswith("."):
                            continue
                        _walk(item, depth + 1)
                    elif item.suffix == ".py":
                        python_files.append(item)
            except (PermissionError, OSError):
                pass

        _walk(project_path)
        return sorted(python_files)
