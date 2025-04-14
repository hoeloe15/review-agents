"""
Plugins for the Review Writer Agent System

This package contains plugins that provide specialized functionality
for the Review Writer Agent System, enabling agents to perform
specific tasks related to review generation and management.

Available plugins:
- ReviewPlugin: Functions for review synthesis and analysis
"""

from src.agents.review_writer.plugins.review_plugin import ReviewPlugin

__all__ = [
    'ReviewPlugin',
] 