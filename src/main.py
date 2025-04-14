#!/usr/bin/env python3
"""
Review Writer System - Main entry point

This script runs a system of agents that generate
comprehensive reviews based on a hardcoded prompt.
"""

import asyncio
import logging
from typing import List, Dict, Any

# Remove incorrect import
# from plugins.review_plugin import ReviewPlugin 

# Add correct import
from review_system import ReviewSystem

# Import ChatHistory
from semantic_kernel.contents import ChatHistory

from utils import format_agent_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def generate_review(prompt: str) -> ChatHistory:
    """
    Generate a comprehensive review based on the provided prompt.
    
    Args:
        prompt: The prompt to generate a review for
        
    Returns:
        The full ChatHistory object containing the agent conversation.
    """
    logger.info(f"Starting review generation for prompt: {prompt}")
    
    # Initialize the review system CORRECTLY
    review_system = ReviewSystem()
    
    # --- Diagnostic Logging --- 
    logger.info(f"Type of review_system: {type(review_system)}")
    logger.info(f"Type of review_system.generate_review: {type(review_system.generate_review)}")
    # --- End Diagnostic Logging ---

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
    
    logger.info(f"Review generation complete with {len(review_system.chat.history.messages)} total messages in history")
    # Return the entire history object
    return review_system.chat.history

async def main():
    """Main entry point for the Review Writer system."""
    # Hardcoded prompt - change this to review different topics
    prompt = "Review the latest Python 3.11 release, focusing on performance improvements, new features, and compatibility considerations."
    
    print("\n" + "=" * 80)
    print(f"Generating review for prompt: {prompt}")
    print("=" * 80 + "\n")
    
    # Generate review and get the history
    final_history = await generate_review(prompt)
    
    print("\n" + "=" * 80)
    print("Full Conversation History:")
    print("=" * 80)
    
    if final_history and final_history.messages:
        for message in final_history.messages:
            # Use a generic name like 'USER' if message.name is None (for initial user prompt)
            agent_name = message.name if message.name else "USER"
            # Skip system messages if any (though we don't explicitly add them)
            if message.role == "system": 
                continue
            print(f"\n{format_agent_message(agent_name, message.content)}\n")
            print("-" * 40) # Shorter separator for history view
    else:
        print("\nNo messages found in the final history.\n")

    print("\n" + "=" * 80)
    print("Review generation process complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # We still need asyncio.run() because the core functions are asynchronous
    asyncio.run(main()) 