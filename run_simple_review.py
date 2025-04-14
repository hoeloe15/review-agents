#!/usr/bin/env python3
"""
Simple Review Writer - Simplified runner script

This is a simplified version of the review writer system that uses a hardcoded prompt
and handles the async operations internally, providing an easier entry point for running reviews.
"""

import asyncio
import logging
import sys

from src.review_system import ReviewSystem
from src.utils import format_agent_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_review(prompt=None):
    """
    Run the review generation process with a given prompt or the default one.
    
    This function wraps the async functionality in a synchronous interface,
    making it easier to run without dealing with asyncio directly.
    
    Args:
        prompt: Optional prompt to override the default
    """
    # Use provided prompt or default
    if not prompt:
        prompt = "Review the latest Python 3.11 release, focusing on performance improvements, new features, and compatibility considerations."
    
    print("\n" + "=" * 80)
    print(f"Generating review for prompt: {prompt}")
    print("=" * 80 + "\n")
    
    # Define async function to run
    async def run_async():
        # Initialize review system
        review_system = ReviewSystem()
        
        # Run review generation
        async for message in review_system.generate_review(prompt):
            if message and message.name:
                # Format and print response
                formatted = format_agent_message(message.name, message.content)
                print(f"\n{formatted}\n")
                print("-" * 80)
        
        print("\n" + "=" * 80)
        print("Review generation complete!")
        print("=" * 80 + "\n")
    
    # Run the async function with asyncio
    asyncio.run(run_async())

if __name__ == "__main__":
    # Allow an optional prompt from command line if provided
    custom_prompt = sys.argv[1] if len(sys.argv) > 1 else None
    run_review(custom_prompt) 