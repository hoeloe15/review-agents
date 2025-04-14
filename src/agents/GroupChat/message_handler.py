"""
Message handling for agent communications.

This module provides functionality for handling, formatting, and broadcasting
messages from agents during document review discussions.
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles message processing, storage, and broadcasting for agent communications.

    This class provides methods to add, broadcast, and format messages for
    agent discussions, ensuring consistent formats for visualization and output.
    """

    def __init__(self):
        """Initialize the message handler."""
        self.messages: List[Dict[str, Any]] = []
        self.visualization_broadcaster: Optional[Callable] = None

    def set_broadcaster(self, broadcaster: Callable) -> None:
        """
        Set the function to broadcast messages to a visualization interface.

        Args:
            broadcaster: A callable that accepts a message dictionary
        """
        self.visualization_broadcaster = broadcaster
        logger.info(
            f"Visualization broadcaster has been set: {broadcaster is not None}"
        )

    async def broadcast_message(self, agent_name: str, content: str) -> None:
        """
        Broadcast a message to the visualization interface if one is set.

        Args:
            agent_name: The name of the agent sending the message
            content: The message content
        """
        if self.visualization_broadcaster:
            try:
                # Ensure content is a string
                if not isinstance(content, str):
                    content = str(content)

                # Truncate very long messages to prevent transmission issues
                if len(content) > 10000:
                    content = content[:10000] + "... (content truncated)"

                # Log before sending
                logger.info(
                    f"Broadcasting message from {agent_name} ({len(content)} chars)"
                )

                # Send the message to the visualization interface
                result = await self.visualization_broadcaster(
                    {
                        "type": "message",
                        "agent": agent_name,
                        "content": content,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Debug log to check result
                logger.info(f"Message broadcast completed with result: {result}")
            except Exception as e:
                logger.error(f"Error broadcasting message from {agent_name}: {str(e)}")
                logger.exception("Full exception details:")
        else:
            logger.warning(
                f"No broadcaster set, message from {agent_name} not broadcasted"
            )

    async def add_message(self, agent_name: str, content: str) -> Dict[str, Any]:
        """
        Add a message to the message store and broadcast it.

        Args:
            agent_name: The name of the agent sending the message
            content: The message content

        Returns:
            The message dictionary that was added
        """
        logger.info(f"Adding message from {agent_name}")

        # Use the agent name as-is (with underscores)
        message = {
            "agent": agent_name,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(message)

        # Log before broadcasting
        logger.info(f"Message stored, now broadcasting from {agent_name}")

        # Broadcast the message
        await self.broadcast_message(agent_name, content)

        # Log after broadcasting
        logger.info(f"Message from {agent_name} processed completely")

        return message

    def clear_messages(self) -> None:
        """Clear all stored messages."""
        self.messages = []

    def format_transcript(self, title: str) -> str:
        """
        Format the messages into a readable transcript.

        Args:
            title: The title of the discussion

        Returns:
            A formatted transcript string
        """
        transcript = f"# Document Review: {title}\n\n"
        for message in self.messages:
            # For transcript format, replace underscores with spaces for better readability
            agent_display = message["agent"].replace("_", " ")
            transcript += f"## {agent_display}:\n{message['content']}\n\n"

        return transcript

    def get_discussion_summary(
        self, max_messages: int = 8, max_chars: int = 200
    ) -> str:
        """
        Get a summary of the recent discussion for use in the recommendation.

        Args:
            max_messages: Maximum number of messages to include
            max_chars: Maximum characters to include from each message

        Returns:
            A string summarizing the discussion
        """
        recent_messages = (
            self.messages[-max_messages:]
            if len(self.messages) > max_messages
            else self.messages
        )
        return "\n\n".join(
            [
                f"{msg['agent'].replace('_', ' ')}: {msg['content'][:max_chars]}..."
                for msg in recent_messages
            ]
        )
