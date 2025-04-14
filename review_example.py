#!/usr/bin/env python3
"""
Example script for the Review Writer system.

This script demonstrates how to use the Review Writer system
to generate comprehensive reviews based on input prompts.
"""

import asyncio
import logging
import argparse
from typing import List, Dict, Any

from src.review_writer import ReviewSystem
from src.review_writer.utils import format_agent_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def generate_review(prompt: str) -> List[Dict[str, Any]]:
    """
    Generate a comprehensive review based on the provided prompt.
    
    Args:
        prompt: The prompt to generate a review for
        
    Returns:
        A list of responses from each agent in the review process
    """
    logger.info(f"Starting review generation for prompt: {prompt}")
    
    # Initialize the review system
    review_system = ReviewSystem()
    
    # Generate review from the prompt
    responses: List[Dict[str, Any]] = []
    
    async for message in review_system.generate_review(prompt):
        if message and message.name:
            response = {
                "agent": message.name,
                "content": message.content,
                "formatted": format_agent_message(message.name, message.content)
            }
            responses.append(response)
            logger.info(f"Received response from {message.name}")
            
            # Print response in real-time
            print(f"\n{response['formatted']}\n")
            print("-" * 80)
    
    logger.info(f"Review generation complete with {len(responses)} total responses")
    return responses

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate a comprehensive review using specialized agents.")
    parser.add_argument(
        "--prompt", 
        type=str,
        help="The prompt to generate a review for",
        default="Review the latest Python 3.11 release, focusing on performance improvements, new features, and compatibility considerations."
    )
    return parser.parse_args()

async def main():
    """Main entry point for the example script."""
    args = parse_arguments()
    
    # Use the provided prompt or the default one
    prompt = args.prompt if args.prompt else "input prompt here"
    
    print("\n" + "=" * 80)
    print(f"Generating review for prompt: {prompt}")
    print("=" * 80 + "\n")
    
    # Generate review
    await generate_review(prompt)
    
    print("\n" + "=" * 80)
    print("Review generation complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 