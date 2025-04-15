#!/usr/bin/env python3
"""
Review Writer System - Main entry point

This script runs a system of agents that generate
comprehensive reviews based on a hardcoded prompt.
"""

import asyncio
import logging
import sys  # Add sys import for console handler
from typing import List, Dict, Any

# Remove incorrect import
# from plugins.review_plugin import ReviewPlugin 

# Add correct import
from review_system import ReviewSystem

# Import ChatHistory
from semantic_kernel.contents import ChatHistory

from utils import format_agent_message

# --- Enhanced Logging Setup ---

# Define log format
log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# Create a root logger instance
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG) # Capture everything at the root level

# Remove existing handlers to avoid duplicate logs if script is re-run in interactive env
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# --- Console Handler (INFO level) ---
# Shows agent messages and key events on the console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO) # Or set higher (WARNING, ERROR) if too verbose
console_handler.setFormatter(log_format)
root_logger.addHandler(console_handler)

# --- File Handler (DEBUG level) ---
# Logs detailed information, including framework internals, to a file
log_file = "app.log"
file_handler = logging.FileHandler(log_file, mode='w') # 'w' overwrites, 'a' appends
file_handler.setLevel(logging.DEBUG) # Capture all details
file_handler.setFormatter(log_format)
root_logger.addHandler(file_handler)

# Optional: Adjust logging levels for noisy libraries (like httpx)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.connectors.ai").setLevel(logging.INFO) # Can adjust this too

# Get logger for this module AFTER root logger is configured
logger = logging.getLogger(__name__)

# --- End Logging Setup ---

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
    message_count = 0 # Add message counter
    
    # Indicate processing start
    print("\nAgents are processing the request... (Details in app.log)\n")
    
    async for message in review_system.generate_review(prompt):
        message_count += 1
        logger.debug(f"Processing message #{message_count}") # Log message count at DEBUG level
        if message and message.name:
            response = {
                "agent": message.name,
                "content": message.content,
                "formatted": format_agent_message(message.name, message.content)
            }
            responses.append(response)
            logger.info(f"Received response from {message.name}")
            
            # Print minimal update to console
            print(f"  - Response from {message.name} received.")
            # Remove detailed real-time printing
            # print(f"\n{response['formatted']}\n")
            # print("-" * 80)
    
    logger.info(f"Review generation complete with {len(review_system.chat.history.messages)} total messages in history (Processed {message_count} agent turns)")
    # Return the entire history object
    return review_system.chat.history

async def main():
    """Main entry point for the Review Writer system."""
    # Hardcoded prompt - change this to review different topics
    prompt = "Review the latest Python 3.11 release, focusing on performance improvements, new features, and compatibility considerations."
    report_filename = "review_report.md" # Define report filename
    
    print("\n" + "=" * 80)
    print(f"Generating review for prompt: {prompt}")
    print("=" * 80 + "\n")
    
    # Generate review and get the history
    final_history = await generate_review(prompt)
    
    # --- Generate Markdown Report ---
    logger.info(f"Generating Markdown report: {report_filename}")
    try:
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(f"# Review Generation Report\n\n")
            f.write(f"**Prompt:** {prompt}\n\n")
            f.write("## Conversation History\n\n")
            
            if final_history and final_history.messages:
                for message in final_history.messages:
                    agent_name = "UNKNOWN"
                    tool_calls_info = [] # List to hold tool call details for this message
                    
                    if message.role == "user":
                        agent_name = "USER"
                    elif message.name:
                        agent_name = message.name
                        
                    # Check for tool call content within the message
                    # Note: SK typically puts tool calls in specific 'items' of the message content
                    if hasattr(message, 'items') and isinstance(message.items, list):
                        for item in message.items:
                            # Check if the item represents a requested function call (tool call)
                            if hasattr(item, 'function_call'): # Depending on SK version, might be different attribute
                                func_call = item.function_call
                                if func_call and hasattr(func_call, 'name') and hasattr(func_call, 'arguments'):
                                    tool_calls_info.append(f"  - Tool Call Requested: `{func_call.name}`")
                                    # Safely format arguments
                                    args_str = str(func_call.arguments) if func_call.arguments else "{}"
                                    # Prevent overly long arg strings in report
                                    if len(args_str) > 300:
                                        args_str = args_str[:297] + "..."
                                    tool_calls_info.append(f"    - Arguments: `{args_str}`")
                            # Alternative check if structure is different (e.g., list of tool_calls)
                            elif hasattr(item, 'tool_calls') and isinstance(item.tool_calls, list):
                                for tool_call in item.tool_calls:
                                    if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name') and hasattr(tool_call.function, 'arguments'):
                                        tool_calls_info.append(f"  - Tool Call Requested: `{tool_call.function.name}`")
                                        args_str = str(tool_call.function.arguments) if tool_call.function.arguments else "{}"
                                        if len(args_str) > 300:
                                            args_str = args_str[:297] + "..."
                                        tool_calls_info.append(f"    - Arguments: `{args_str}`")
                                
                    # Use format_agent_message utility for consistency
                    formatted_message = format_agent_message(agent_name, message.content)
                    
                    # Write formatted message to file
                    f.write(f"{formatted_message}\n\n")
                    
                    # Write tool call info if any exists for this message
                    if tool_calls_info:
                        f.write("**Tool Calls:**\n")
                        for line in tool_calls_info:
                            f.write(f"{line}\n")
                        f.write("\n")
                        
                    # Add a markdown separator
                    f.write("----------------------------------------\n\n") 
            else:
                f.write("No messages found in the final history.\n")
        logger.info(f"Successfully generated Markdown report: {report_filename}")
    except Exception as e:
        logger.error(f"Failed to generate Markdown report: {e}")
    # --- End Report Generation ---
        
    print("\n" + "=" * 80)
    # Don't print full history to console by default
    # print("Full Conversation History:")
    # print("=" * 80)
    
    # if final_history and final_history.messages:
    #     for message in final_history.messages:
    #         # Use a generic name like 'USER' if message.name is None (for initial user prompt)
    #         agent_name = message.name if message.name else "USER"
    #         # Skip system messages if any (though we don't explicitly add them)
    #         if message.role == "system": 
    #             continue
    #         print(f"\n{format_agent_message(agent_name, message.content)}\n")
    #         print("-" * 40) # Shorter separator for history view
    # else:
    #     print("\nNo messages found in the final history.\n")

    print("\n" + "=" * 80)
    print("Review generation process complete!")
    print(f"Check {report_filename} for the conversation history.") # Point to MD report
    print("Check app.log for detailed execution trace.") 
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # We still need asyncio.run() because the core functions are asynchronous
    asyncio.run(main()) 