"""
Review System - Main orchestrator for review generation

This module provides the ReviewSystem class that coordinates specialized agents
to generate comprehensive reviews.
"""

import logging
from typing import AsyncIterable, List

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.chat_history import ChatHistory

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
        
        # Store agents in a sequence for manual orchestration
        self.agent_sequence: List[ChatCompletionAgent] = [
            self.review_coordinator,
            self.tech_reviewer,
            self.relevance_analyst,
            self.implementation_analyst
        ]
        logger.debug(f"Agent sequence defined: {[agent.name for agent in self.agent_sequence]}")
    
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
    
    async def generate_review(self, prompt: str) -> ChatHistory:
        """
        Generate a comprehensive review based on the provided prompt using manual orchestration.
        
        Args:
            prompt: The prompt to generate a review for
            
        Returns:
           ChatHistory: The complete chat history after orchestration.
        """
        logger.info(f"Generating review for prompt using manual orchestration: {prompt}")
        
        # Define maximum turns (matching previous strategy)
        max_turns = 9 
        turn_count = 0
        
        # Create a new chat history for this review
        history = ChatHistory()
        logger.debug("Created new ChatHistory for this request.")

        # Add the initial user prompt
        history.add_user_message(prompt)
        logger.debug("Added user prompt to chat history.")

        # Manual Orchestration Loop
        while turn_count < max_turns:
            # Determine the current agent based on the sequence
            current_agent_index = turn_count % len(self.agent_sequence)
            current_agent = self.agent_sequence[current_agent_index]
            turn_count += 1
            
            logger.info(f"Turn {turn_count}/{max_turns}: Invoking agent -> {current_agent.name}")

            try:
                # Invoke the agent with the current history
                # Process the async generator to get the final message(s)
                agent_response_messages = []
                # Use positional argument for history based on error analysis
                async for message_chunk in current_agent.invoke(history):
                     agent_response_messages.append(message_chunk)
                
                # Assume the last message in the list is the final, complete one for this turn
                if not agent_response_messages:
                    logger.warning(f"Agent {current_agent.name} did not yield any messages. Skipping turn.")
                    continue
                    
                final_message: ChatMessageContent = agent_response_messages[-1]
                
                if final_message is None or not final_message.content:
                    logger.warning(f"Agent {current_agent.name} returned an empty final message content. Skipping turn.")
                    continue
                
                # Ensure the message has the agent's name (should be set by ChatCompletionAgent)
                if not final_message.name:
                    final_message.name = current_agent.name
                    
                # Add the agent's response to the history
                # Use the specific message object returned by the agent
                history.add_message(message=final_message)
                logger.debug(f"Added message from {current_agent.name} to history.")

            except Exception as e:
                logger.error(f"Error invoking agent {current_agent.name} on turn {turn_count}: {e}", exc_info=True)
                # Decide how to handle errors: stop, skip agent, add error message to history?
                # For now, we'll stop the process on error.
                break
                
        logger.info(f"Manual orchestration finished after {turn_count} turns.")
        return history # Return the final history object

