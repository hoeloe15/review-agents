"""
Utility Functions - Helper functions for the Review Writer system

This module provides utility functions for working with reviews,
formatting messages, and other helper operations.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def format_agent_message(agent_name: str, message: str) -> str:
    """
    Format an agent's message with a header showing the agent name.
    
    Args:
        agent_name: The name of the agent
        message: The message content
        
    Returns:
        A formatted message with the agent name as header
    """
    return f"## {agent_name}\n\n{message}"

def extract_review_sections(full_review: str) -> Dict[str, str]:
    """
    Extract sections from a full review text.
    
    Args:
        full_review: The full review text with markdown sections
        
    Returns:
        A dictionary with section titles as keys and section content as values
    """
    sections = {}
    current_section = "preamble"
    current_content = []
    
    # Split text by lines
    lines = full_review.split("\n")
    
    for line in lines:
        # Check if the line is a section header (starts with # or ##)
        if line.startswith("# ") or line.startswith("## "):
            # Save previous section content if we've been collecting a section
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
                current_content = []
            
            # Get new section title
            current_section = line.lstrip("#").strip()
        else:
            # Add line to current section
            current_content.append(line)
    
    # Add the final section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return sections

def create_simplified_review(full_review: str, max_length: int = 500) -> str:
    """
    Create a simplified version of the review for scenarios requiring brevity.
    
    Args:
        full_review: The full review text
        max_length: Maximum length of the simplified review
        
    Returns:
        A simplified version of the review
    """
    sections = extract_review_sections(full_review)
    
    # Prioritize sections to include
    summary = sections.get("Executive Summary", "")
    conclusion = sections.get("Conclusion", "")
    
    simplified = f"{summary}\n\n{conclusion}"
    
    # Truncate if necessary
    if len(simplified) > max_length:
        simplified = simplified[:max_length-3] + "..."
    
    return simplified 