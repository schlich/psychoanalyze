"""CLI entrypoint for psychoanalyze."""

import argparse
import sys
from importlib.metadata import version


def app() -> None:
    """Main CLI entrypoint for psychoanalyze."""
    parser = argparse.ArgumentParser(
        prog="psychoanalyze",
        description="A tool for psychoanalysis",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('psychoanalyze')}",
    )
    
    # Parse arguments (args currently unused, but reserved for future subcommands)
    parser.parse_args()


if __name__ == "__main__":
    app()
