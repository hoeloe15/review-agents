"""
Review Writer Agent System

A system of semantic kernel agents that collaborate to generate comprehensive reviews.
This system consists of specialized agents that analyze different aspects of a product
or technology, coordinated by a main reviewer agent.

Available components:
- ReviewWriterSystem: The main class for generating reviews using specialized agents
- Plugins: Functions for review synthesis, extraction, and formatting
- Utilities: Helper functions for setting up and running the review system
"""

from src.agents.review_writer.review_writer_agent import ReviewWriterSystem
from src.agents.review_writer.review_utils import (
    setup_kernel_with_plugins,
    format_agent_message,
    extract_review_sections,
    create_simplified_review
)

__all__ = [
    'ReviewWriterSystem',
    'setup_kernel_with_plugins',
    'format_agent_message',
    'extract_review_sections',
    'create_simplified_review',
] 