"""
Document review chat implementation using the StatefulGroupChat.

This module provides a specialized implementation for document reviews
using the stateful group chat for better agent interactions.
"""

import logging
from typing import Optional, List, Callable

from semantic_kernel import Kernel
from semantic_kernel.contents.utils.author_role import AuthorRole

from .agent_config import (
    get_initial_prompt_template, 
    get_recommendation_prompt_template,
    get_fallback_recommendation_template,
)
from .agent_factory import create_all_agents, create_recommendation_agent
from .conversation_state import ConversationState
from .message_handler import MessageHandler
from .stateful_group_chat import StatefulGroupChat

logger = logging.getLogger(__name__)


class DocumentReviewChat:
    """
    Manages a document review discussion among multiple agents.
    
    This class uses the StatefulGroupChat to create discussions about documents,
    with specialized handling for document reviews and recommendations.
    """
    
    def __init__(
        self, 
        kernel: Optional[Kernel] = None,
        moderator_name: Optional[str] = None,
        recommendation_agent_name: Optional[str] = None
    ):
        """
        Initialize the document review chat.
        
        Args:
            kernel: Optional kernel instance (will create one if not provided)
            moderator_name: Name of the agent that should moderate the discussion
            recommendation_agent_name: Name of the agent to generate recommendations
        """
        # Create or use provided kernel
        self.kernel = kernel if kernel is not None else self._create_kernel()
        
        # Create message handler
        self.message_handler = MessageHandler()
        
        # Create all agents
        self.agents = create_all_agents(self.kernel)
        self.agent_names = list(self.agents.keys())
        
        # Determine moderator and recommendation agent
        self.moderator_name = moderator_name or self.agent_names[0]  # Default to first agent
        self.recommendation_agent_name = recommendation_agent_name or self.moderator_name
        
        # Create conversation state
        self.state = ConversationState()
        
        # Create the stateful group chat
        self.group_chat = StatefulGroupChat(
            agents=list(self.agents.values()),
            kernel=self.kernel,
            initial_agent_name=self.moderator_name,
            state=self.state,
            message_handler=self.message_handler
        )
    
    def set_broadcaster(self, broadcaster: Callable) -> None:
        """
        Set the function to broadcast messages to a visualization interface.
        
        Args:
            broadcaster: A callable that accepts message dictionaries
        """
        self.message_handler.set_broadcaster(broadcaster)
        logger.info("Visualization broadcaster has been set up")
    
    def _create_kernel(self) -> Kernel:
        """
        Create a Semantic Kernel instance with appropriate services.
        
        Returns:
            Configured Semantic Kernel instance
        """
        try:
            from .kernel_provider import KernelProvider
            return KernelProvider.get_kernel()
        except (ImportError, ValueError) as e:
            logger.error(f"Error creating kernel: {e}")
            raise
    
    async def discuss_document(self, document: str, title: str, rounds: int = 2) -> str:
        """
        Conduct a discussion about the document among the agents.
        
        Args:
            document: The document text to discuss
            title: The title of the document
            rounds: Number of rounds (not directly used, controlled by termination)
            
        Returns:
            A string containing the discussion transcript
            
        Raises:
            ValueError: If document or title is empty
        """
        if not document:
            raise ValueError("Document text cannot be empty")
            
        if not title:
            title = "Untitled Document"
        
        # Reset for a new discussion
        await self.group_chat.reset()
        
        # Create the initial prompt with document
        initial_prompt = get_initial_prompt_template().format(
            title=title,
            document=document,
            lead_advisor=self.moderator_name
        )
        
        logger.info(f"Starting agent discussion for document: {title}")
        
        # Start the discussion
        async for _ in self.group_chat.invoke(initial_prompt):
            pass  # Process all messages
        
        # Return the formatted transcript
        return self.message_handler.format_transcript(title)
    
    async def get_recommendation(self, document: str, title: str) -> str:
        """
        Generate a final recommendation based on the document and discussion.
        
        Args:
            document: The document text
            title: The document title
            
        Returns:
            A recommendation string
            
        Raises:
            ValueError: If document or title is empty
        """
        if not document:
            raise ValueError("Document text cannot be empty")
            
        if not title:
            title = "Untitled Document"
        
        try:
            # Get discussion summary
            discussion_summary = self.message_handler.get_discussion_summary()
            
            # Create recommendation prompt
            recommendation_prompt = get_recommendation_prompt_template().format(
                title=title,
                discussion_summary=discussion_summary
            )
            
            # Create recommendation agent
            recommendation_agent = create_recommendation_agent(
                self.kernel,
                self.recommendation_agent_name
            )
            
            # Create a separate group chat for the recommendation
            recommendation_chat = StatefulGroupChat(
                agents=[recommendation_agent],
                kernel=self.kernel
            )
            
            # Get recommendation
            recommendation = ""
            async for response in recommendation_chat.invoke(recommendation_prompt, include_state=False):
                if response and response.role == AuthorRole.ASSISTANT:
                    recommendation = response.content
                    break
            
            return recommendation or self._get_fallback_recommendation(title)
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            logger.exception("Full exception details")
            return self._get_fallback_recommendation(title)
    
    def _get_fallback_recommendation(self, title: str) -> str:
        """
        Get a fallback recommendation when an error occurs.
        
        Args:
            title: The document title
            
        Returns:
            A fallback recommendation string
        """
        return get_fallback_recommendation_template().format(title=title) 