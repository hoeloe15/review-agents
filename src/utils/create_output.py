"""
Utility functions for generating output files for review results.
"""

import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


def save_review_markdown(results: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate and save a Markdown file with the review results from a JSON structure.

    Args:
        results: Dictionary containing the review results
        output_path: Optional custom output path

    Returns:
        The path to the saved Markdown file
    """
    # Extract title from results or use default
    title = results.get("title", "Technology_Review")

    # Start building the markdown content
    markdown_content = f"# {title} - Review Results\n\n"

    # Add the agent discussion
    if "agent_discussion" in results:
        markdown_content += "## Agent Discussion\n\n"
        markdown_content += results["agent_discussion"] + "\n\n"

    # Add the final recommendation
    if "final_recommendation" in results:
        markdown_content += "\n\n---\n\n## 🎯 Final Recommendation\n\n"
        markdown_content += results["final_recommendation"]

    # Ensure the directory exists
    output_dir = "/workspaces/pbod/review_results"
    os.makedirs(output_dir, exist_ok=True)

    # Determine file path
    if output_path:
        file_path = output_path
    else:
        file_path = f"{output_dir}/{title.replace(' ', '_')}_review.md"

    try:
        with open(file_path, "w") as f:
            f.write(markdown_content)
        logger.info(f"Review results saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving review results to Markdown file: {e}")
        return ""
