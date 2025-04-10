"""
Technology Review Board - Main entry point that always starts the visualization server.
"""

import asyncio
import logging
from pathlib import Path

from agents.orchestration import DocumentReviewOrchestrator
from visualization.server import start_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the Technology Review Board application."""
    try:
        # Start the visualization server
        server_url = start_server()
        
        print(f"\n{'='*70}")
        print("Technology Review Board running at:")
        print(f"{server_url}")
        print("Open this URL in a browser to analyze documents")
        print(f"{'='*70}\n")
        
        # Keep the main process running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nApplication stopped. Goodbye!")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        logger.exception("Full exception details:")


if __name__ == "__main__":
    asyncio.run(main())
