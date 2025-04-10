"""
Conversation state tracking for multi-agent discussions.

This module provides classes for tracking and managing state in multi-agent conversations,
making agent selection and termination decisions more informed and effective.
"""

import logging
from typing import Dict, Any, Optional, Set, List

logger = logging.getLogger(__name__)


class ConversationState:
    """
    Tracks and manages the state of a multi-agent conversation.
    
    This class provides methods to update state after messages, format state information
    for prompts, and track various aspects of the conversation including speakers,
    message counts, and custom state variables.
    """
    
    def __init__(self):
        """Initialize the conversation state with default values."""
        # Core state tracking
        self.message_count = 0
        self.last_speaker = None
        self.speakers_so_far = set()
        
        # Custom state storage
        self.custom_state = {}
    
    def update_after_message(self, agent_name: str) -> None:
        """
        Update the conversation state after a new message.
        
        Args:
            agent_name: The name of the agent who just spoke
        """
        self.message_count += 1
        self.last_speaker = agent_name
        self.speakers_so_far.add(agent_name)
        logger.info(f"State updated: {agent_name} spoke, message #{self.message_count}")
    
    def set_custom_state(self, key: str, value: Any) -> None:
        """
        Set a custom state variable.
        
        Args:
            key: The name of the state variable
            value: The value to store
        """
        self.custom_state[key] = value
        logger.info(f"Custom state set: {key}={value}")
    
    def get_custom_state(self, key: str, default: Any = None) -> Any:
        """
        Get a custom state variable.
        
        Args:
            key: The name of the state variable
            default: Default value if the key doesn't exist
            
        Returns:
            The stored value or the default
        """
        return self.custom_state.get(key, default)
    
    def format_as_prompt(self) -> str:
        """
        Format the conversation state as a string for inclusion in prompts.
        
        Returns:
            A formatted string representation of the state
        """
        # Start with basic state information
        state_lines = [
            "=== CONVERSATION STATE ===",
            f"LAST SPEAKER: {self.last_speaker or 'none'}",
            f"MESSAGE COUNT: {self.message_count}",
            f"SPEAKERS SO FAR: {', '.join(sorted(self.speakers_so_far)) if self.speakers_so_far else 'none'}"
        ]
        
        # Add any custom state variables
        if self.custom_state:
            state_lines.append("CUSTOM STATE:")
            for key, value in self.custom_state.items():
                # Format value based on type
                if isinstance(value, (list, set)):
                    formatted_value = ", ".join(str(v) for v in value) 
                else:
                    formatted_value = str(value)
                state_lines.append(f"  {key.upper()}: {formatted_value}")
        
        state_lines.append("========================")
        
        return "\n".join(state_lines)
    
    def has_all_agents_spoken(self, agent_names: List[str]) -> bool:
        """
        Check if all the specified agents have spoken at least once.
        
        Args:
            agent_names: List of agent names to check
            
        Returns:
            True if all agents have spoken, False otherwise
        """
        return all(agent in self.speakers_so_far for agent in agent_names)
    
    def reset(self) -> None:
        """Reset the conversation state to initial values."""
        self.message_count = 0
        self.last_speaker = None
        self.speakers_so_far = set()
        self.custom_state = {}
        logger.info("Conversation state has been reset") 