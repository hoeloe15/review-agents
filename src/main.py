#!/usr/bin/env python3
"""
Review Writer System - Main entry point

This script runs a system of agents that generate
comprehensive reviews based on a hardcoded prompt.
"""

import asyncio
import logging
from typing import List, Dict, Any

from semantic_kernel.contents.chat_message_content import ChatMessageContent

from review_system import ReviewSystem
from utils import format_agent_message

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

async def main():
    """Main entry point for the Review Writer system."""
    # Hardcoded prompt - change this to review different topics
    prompt = "Review the latest Python 3.11 release, focusing on performance improvements, new features, and compatibility considerations."
    
    print("\n" + "=" * 80)
    print(f"Generating review for prompt: {prompt}")
    print("=" * 80 + "\n")
    
    # Generate review
    await generate_review(prompt)
    
    print("\n" + "=" * 80)
    print("Review generation complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # We still need asyncio.run() because the core functions are asynchronous
    asyncio.run(main()) 