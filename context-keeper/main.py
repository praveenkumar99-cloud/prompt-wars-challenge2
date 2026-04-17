import sys
from cli import run_cli

def example_context_keeper():
    """
    Example code to show the new functionality.
    This effectively wraps the CLI runner.
    """
    try:
        run_cli()
    except SystemExit as e:
        # Prevent sys.exit from closing the interpreter during testing
        if e.code != 0:
            raise

def main():
    """
    Main method is the entry point to showcase functionality.
    It simply calls the example method as per guidelines.
    """
    example_context_keeper()

if __name__ == "__main__":
    main()
