"""
Main entry point for the Review Writer Agent system.

This module provides a simple interface for using the Review Writer Agent system
to generate comprehensive reviews based on input prompts.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from src.agents.review_writer.review_writer_agent import ReviewWriterSystem
from src.agents.review_writer.review_utils import format_agent_message
from semantic_kernel.contents.chat_message_content import ChatMessageContent

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
    
    # Initialize the review writer system
    review_system = ReviewWriterSystem()
    
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
    
    logger.info(f"Review generation complete with {len(responses)} total responses")
    return responses

async def main():
    """Main entry point for the Review Writer Agent system."""
    # Example prompt - this would be replaced with actual input
    example_prompt = "input prompt here"
    
    # Generate review
    responses = await generate_review(example_prompt)
    
    # Print responses (for demonstration purposes)
    print("\n\n=========== REVIEW GENERATION RESULTS ===========\n")
    for response in responses:
        print(f"\n{response['formatted']}\n")
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 