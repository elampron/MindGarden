"""
MindGarden main entry point.
"""

from mindgarden.core.logging import setup_logging
from mindgarden.cli.main import main as cli_main


def main():
    """Run MindGarden."""
    # Initialize logging
    logger = setup_logging()
    logger.info("Starting MindGarden")
    
    # Run the CLI app
    cli_main()


if __name__ == "__main__":
    main()
