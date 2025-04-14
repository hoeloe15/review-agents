"""
Base agent class that defines the common interface for agents.

This module provides the base class for all agents in the system,
defining a common interface for agent operations.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the system.
    
    This abstract class defines the interface that all agent implementations
    should follow. It provides basic functionality for agent identification
    and a default process method that subclasses can override.
    """

    def __init__(self, name: str):
        """
        Initialize the agent with a name.

        Args:
            name: The name of the agent used for identification
            
        Raises:
            ValueError: If name is empty or None
        """
        if not name:
            raise ValueError("Agent name cannot be empty")
            
        self.name = name
        logger.debug(f"Initialized agent: {name}")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        This is the main method that subclasses should override to implement
        their specific processing logic.

        Args:
            input_data: Dictionary with input data for processing

        Returns:
            Dictionary with the processed results
            
        Raises:
            NotImplementedError: If subclass doesn't override this method
                when it should be overridden
        """
        # Default implementation that subclasses can override if needed
        logger.warning(f"Agent {self.name} using default processing implementation. "
                      "Subclasses should override this method.")
        return {
            "agent": self.name, 
            "message": "Default agent processing - this method should be overridden"
        }

    def get_name(self) -> str:
        """
        Get the name of the agent.
        
        Returns:
            The agent's name
        """
        return self.name
        
    def __str__(self) -> str:
        """
        Get string representation of the agent.
        
        Returns:
            String representation including the agent's name
        """
        return f"Agent({self.name})"
        
    def __repr__(self) -> str:
        """
        Get programmer representation of the agent.
        
        Returns:
            Representation including the agent's class and name
        """
        return f"{self.__class__.__name__}(name='{self.name}')"
