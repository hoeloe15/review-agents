#!/usr/bin/env python3
"""
Run a review directly using the Review Writer System.

This script serves as a convenient entry point for running a review
directly from the command line, without starting the web server.
"""

import sys
import subprocess
import argparse
import os

def main():
    """Main entry point for running a review."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a review using the Review Writer System")
    parser.add_argument(
        "--prompt", 
        type=str, 
        help="The prompt to use for review generation"
    )
    args = parser.parse_args()
    
    # Get the absolute path to the main.py script
    main_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "main.py")
    
    # Build the command to run
    cmd = [sys.executable, main_script_path, "--run-review"]
    if args.prompt:
        cmd.extend(["--prompt", args.prompt])
    
    # Run the script
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main() 