"""
Review System - Main orchestrator for review generation

This module provides the ReviewSystem class that coordinates specialized agents
to generate comprehensive reviews.
"""

import logging
from typing import AsyncIterable

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    SequentialSelectionStrategy, 
    DefaultTerminationStrategy
)
from semantic_kernel.contents.chat_message_content import ChatMessageContent

from kernel_provider import KernelProvider
from prompts import (
    TECH_REVIEWER_PROMPT,
    RELEVANCE_ANALYST_PROMPT,
    IMPLEMENTATION_ANALYST_PROMPT,
    COORDINATOR_PROMPT,
)

logger = logging.getLogger(__name__)

# Define agent names
MAIN_REVIEWER_NAME = "ReviewCoordinator"
TECH_REVIEWER_NAME = "TechnologyReviewer"
RELEVANCE_REVIEWER_NAME = "RelevanceAnalyst" 
IMPLEMENTATION_REVIEWER_NAME = "ImplementationAnalyst"

class ReviewSystem:
    """
    A system of agents that collaborate to generate comprehensive reviews.
    
    This system consists of multiple specialized agents that analyze different aspects
    of a product or technology, coordinated by a main reviewer agent that assembles
    their findings into a comprehensive review.
    """
    
    def __init__(self):
        """Initialize the review system with specialized agents."""
        # Get a kernel instance from the provider
        self.kernel = KernelProvider.get_kernel()
        logger.debug("Kernel instance obtained.")
        
        # Create the specialized agents
        logger.debug("Creating specialized agents...")
        self.tech_reviewer = self._create_tech_reviewer()
        self.relevance_analyst = self._create_relevance_analyst()
        self.implementation_analyst = self._create_implementation_analyst()
        self.review_coordinator = self._create_review_coordinator()
        
        # Create agent group chat with all agents
        self.chat = self._create_group_chat()
    
    def _create_tech_reviewer(self) -> ChatCompletionAgent:
        """Create the technology reviewer agent."""
        logger.debug(f"Creating agent: {TECH_REVIEWER_NAME}")
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=TECH_REVIEWER_NAME,
            instructions=TECH_REVIEWER_PROMPT
        )
    
    def _create_relevance_analyst(self) -> ChatCompletionAgent:
        """Create the relevance and alternatives analyst agent."""
        logger.debug(f"Creating agent: {RELEVANCE_REVIEWER_NAME}")
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=RELEVANCE_REVIEWER_NAME,
            instructions=RELEVANCE_ANALYST_PROMPT
        )
    
    def _create_implementation_analyst(self) -> ChatCompletionAgent:
        """Create the implementation analyst agent."""
        logger.debug(f"Creating agent: {IMPLEMENTATION_REVIEWER_NAME}")
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=IMPLEMENTATION_REVIEWER_NAME,
            instructions=IMPLEMENTATION_ANALYST_PROMPT
        )
    
    def _create_review_coordinator(self) -> ChatCompletionAgent:
        """Create the main review coordinator agent."""
        logger.debug(f"Creating agent: {MAIN_REVIEWER_NAME}")
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=MAIN_REVIEWER_NAME,
            instructions=COORDINATOR_PROMPT
        )
    
    def _create_group_chat(self) -> AgentGroupChat:
        """Create the agent group chat with all specialized agents."""
        # Define the agent order for sequential execution (Coordinator starts)
        logger.debug("Defining agent sequence for group chat.")
        agent_sequence = [
            self.review_coordinator,
            self.tech_reviewer,
            self.relevance_analyst,
            self.implementation_analyst
        ]

        # Create agent group chat using simpler strategies
        logger.debug("Creating AgentGroupChat with SequentialSelectionStrategy and DefaultTerminationStrategy.")
        return AgentGroupChat(
            agents=agent_sequence,
            # Strategy to cycle through agents in the defined order
            selection_strategy=SequentialSelectionStrategy(
                agents=agent_sequence,
                # Set initial_agent explicitly if needed, though Sequential often starts from the beginning
                initial_agent=self.review_coordinator
            ),
            # Strategy to terminate after a fixed number of turns
            termination_strategy=DefaultTerminationStrategy(
                # Allow coordinator start + 2 rounds for each specialist (1 + 4 + 4 = 9 turns)
                maximum_iterations=9 
            ),
        )
    
    async def generate_review(self, prompt: str) -> AsyncIterable[ChatMessageContent]:
        """
        Generate a comprehensive review based on the provided prompt.
        
        Args:
            prompt: The prompt to generate a review for
            
        Yields:
            ChatMessageContent: Responses from the agents
        """
        logger.info(f"Generating review for prompt: {prompt}")
        
        # Reset the chat for a new conversation
        logger.debug("Resetting AgentGroupChat history.")
        await self.chat.reset()
        
        # Add the user prompt to the chat
        logger.debug("Adding user prompt to chat history.")
        # NOTE: The initial user prompt doesn't count towards maximum_iterations
        # The first iteration starts when the first agent (Coordinator) responds.
        await self.chat.add_chat_message(message=prompt)
        
        # Invoke the chat and yield responses
        logger.debug("Invoking agent chat...")
        async for response in self.chat.invoke():
            if response is None or not response.name:
                logger.debug("Received empty response, skipping.")
                continue
            logger.debug(f"Yielding response from {response.name}.")
            yield response 