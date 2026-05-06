"""Entry point for running sentrux as a module."""

import sys

import click

from sentrux.cli.main import cli
from sentrux.mcp.server import run_mcp_server


@click.command()
@click.option("--mcp", is_flag=True, help="Run as MCP server")
def main(mcp: bool):
    """Sentrux entry point."""
    if mcp:
        run_mcp_server()
    else:
        # Run CLI
        sys.argv = [sys.argv[0]] + sys.argv[2:]  # Remove --mcp flag
        cli()


if __name__ == "__main__":
    main()
