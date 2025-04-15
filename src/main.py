#!/usr/bin/env python3
"""
Review Writer System - Main entry point

This script starts the FastAPI server for the multi-agent review demo.
"""

import logging
import sys

# Import the server module
from server import start_server

# --- Logging Setup ---
# Define log format
log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# Create a root logger instance
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Remove existing handlers to avoid duplicate logs
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Console Handler (INFO level)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
root_logger.addHandler(console_handler)

# File Handler (DEBUG level)
log_file = "app.log"
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
root_logger.addHandler(file_handler)

# Adjust logging levels for noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.connectors.ai").setLevel(logging.INFO)

# Get logger for this module
logger = logging.getLogger(__name__)
# --- End Logging Setup ---

def main():
    """Main entry point for the Review Writer system."""
    print("\n" + "=" * 80)
    print("Starting Multi-Agent Review System Demo")
    print("=" * 80)
    print("\nOnce the server starts, open your browser and go to:")
    print("http://localhost:8000")
    print("\nPress Ctrl+C to stop the server\n")
    
    logger.info("Starting FastAPI server for Multi-Agent Review System Demo")
    
    # Start the FastAPI server
    start_server()

if __name__ == "__main__":
    main() 