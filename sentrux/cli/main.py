"""CLI interface for Sentrux."""

import json
from pathlib import Path
from typing import Optional

import click

from sentrux.core.analyzer import ProjectAnalyzer
from sentrux.core.rules import RulesEngine
from sentrux.utils.config import ConfigLoader


@click.group()
@click.version_option()
def cli():
    """Sentrux - Structural quality analysis for Python projects."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def scan(path: str, output_json: bool):
    """Analyze code quality of a Python project."""
    try:
        project_path = Path(path)
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()

        if output_json:
            click.echo(json.dumps(analysis.to_dict(), indent=2))
        else:
            _print_analysis_summary(analysis)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def check(path: str, output_json: bool):
    """Check if project meets architectural rules."""
    try:
        project_path = Path(path)

        # Load rules
        rules = ConfigLoader.load_rules(project_path)

        # Analyze
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()

        # Check rules
        engine = RulesEngine(rules)
        violations = engine.check_violations(analysis)

        if output_json:
            result = {
                "path": str(project_path),
                "quality_score": analysis.quality_score.to_dict()
                if analysis.quality_score
                else None,
                "violations": violations,
                "passed": len(violations) == 0,
            }
            click.echo(json.dumps(result, indent=2))
        else:
            if violations:
                click.echo("❌ Violations found:")
                for violation in violations:
                    click.echo(f"  - {violation}")
                raise SystemExit(1)
            else:
                click.echo("✅ All rules passed")

    except SystemExit:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--save", is_flag=True, help="Save current metrics as baseline")
def gate(path: str, save: bool):
    """Check quality against baseline or save new baseline."""
    try:
        project_path = Path(path)

        # Analyze
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()

        if save:
            # Save baseline
            if analysis.quality_score:
                baseline = analysis.quality_score.to_dict()
                ConfigLoader.save_baseline(project_path, baseline)
                click.echo(f"Baseline saved: {analysis.quality_score.overall_score}/10000")
        else:
            # Compare against baseline
            baseline = ConfigLoader.load_baseline(project_path)

            if not baseline:
                click.echo("No baseline found. Use --save to create one.")
                raise SystemExit(1)

            if analysis.quality_score:
                current_score = analysis.quality_score.overall_score
                baseline_score = baseline.get("overall_score", 0)

                click.echo(f"Baseline:  {baseline_score}/10000")
                click.echo(f"Current:   {current_score}/10000")

                if current_score < baseline_score:
                    diff = baseline_score - current_score
                    click.echo(f"⚠️  Regression: -{diff} points")
                    raise SystemExit(1)
                elif current_score > baseline_score:
                    improvement = current_score - baseline_score
                    click.echo(f"✅ Improvement: +{improvement} points")
                else:
                    click.echo("✅ No change")

    except SystemExit:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


def _print_analysis_summary(analysis) -> None:
    """Print analysis summary in human-readable format."""
    click.echo(f"\nProject: {analysis.project_path}")
    click.echo(f"Files analyzed: {len(analysis.files)}")

    if analysis.quality_score:
        score = analysis.quality_score
        click.echo(f"\n📊 Quality Score: {score.overall_score}/10000")
        click.echo(f"   Modularity:     {score.modularity:.2f}")
        click.echo(f"   Acyclicity:     {score.acyclicity:.2f}")
        click.echo(f"   Depth:          {score.depth:.2f}")
        click.echo(f"   Equality:       {score.equality:.2f}")
        click.echo(f"   Redundancy:     {score.redundancy:.2f}")

    if analysis.rules_violations:
        click.echo(f"\n⚠️  Rule Violations: {len(analysis.rules_violations)}")
        for violation in analysis.rules_violations:
            click.echo(f"   - {violation}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
