#!/usr/bin/env python3
"""
Start the FastAPI server for the Multi-Agent Review System Demo.

This script serves as the entry point for running the web server that hosts
the frontend and backend components of the multi-agent review system.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the server."""
    logger.info("Starting the Multi-Agent Review System Server")
    
    # Add the current directory to the path if it's not already there
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    
    # Import and start the server directly
    try:
        from src.server import start_server
        start_server()
    except ImportError as e:
        logger.error(f"Error importing server module: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 