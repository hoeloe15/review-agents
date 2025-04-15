"""
Review System - Main orchestrator for review generation

This module provides the ReviewSystem class that coordinates specialized agents
to generate comprehensive reviews.
"""

import logging
from typing import AsyncIterable

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.functions import KernelFunctionFromPrompt

from kernel_provider import KernelProvider
from prompts import (
    TECH_REVIEWER_PROMPT,
    RELEVANCE_ANALYST_PROMPT,
    IMPLEMENTATION_ANALYST_PROMPT,
    COORDINATOR_PROMPT,
    SELECTION_PROMPT, 
    TERMINATION_PROMPT
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
        
        # Create the specialized agents
        self.tech_reviewer = self._create_tech_reviewer()
        self.relevance_analyst = self._create_relevance_analyst()
        self.implementation_analyst = self._create_implementation_analyst()
        self.review_coordinator = self._create_review_coordinator()
        
        # Create agent group chat with all agents
        self.chat = self._create_group_chat()
        
        # Add a system message to the chat history
        self._add_system_message()
    
    def _create_tech_reviewer(self) -> ChatCompletionAgent:
        """Create the technology reviewer agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=TECH_REVIEWER_NAME,
            instructions=TECH_REVIEWER_PROMPT
        )
    
    def _create_relevance_analyst(self) -> ChatCompletionAgent:
        """Create the relevance and alternatives analyst agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=RELEVANCE_REVIEWER_NAME,
            instructions=RELEVANCE_ANALYST_PROMPT
        )
    
    def _create_implementation_analyst(self) -> ChatCompletionAgent:
        """Create the implementation analyst agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=IMPLEMENTATION_REVIEWER_NAME,
            instructions=IMPLEMENTATION_ANALYST_PROMPT
        )
    
    def _create_review_coordinator(self) -> ChatCompletionAgent:
        """Create the main review coordinator agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=MAIN_REVIEWER_NAME,
            instructions=COORDINATOR_PROMPT
        )
    
    def _create_selection_function(self) -> KernelFunctionFromPrompt:
        """Create a function to determine which agent should respond next."""
        return KernelFunctionFromPrompt(
            function_name="selection",
            prompt=SELECTION_PROMPT.format(
                main_reviewer_name=MAIN_REVIEWER_NAME,
                tech_reviewer_name=TECH_REVIEWER_NAME,
                relevance_reviewer_name=RELEVANCE_REVIEWER_NAME,
                implementation_reviewer_name=IMPLEMENTATION_REVIEWER_NAME
            )
        )
    
    def _create_termination_function(self) -> KernelFunctionFromPrompt:
        """Create a function to determine when the review is complete."""
        return KernelFunctionFromPrompt(
            function_name="termination",
            prompt=TERMINATION_PROMPT.format(
                main_reviewer_name=MAIN_REVIEWER_NAME,
                tech_reviewer_name=TECH_REVIEWER_NAME,
                relevance_reviewer_name=RELEVANCE_REVIEWER_NAME,
                implementation_reviewer_name=IMPLEMENTATION_REVIEWER_NAME
            )
        )
    
    def _create_group_chat(self) -> AgentGroupChat:
        """Create the agent group chat with all specialized agents."""
        selection_function = self._create_selection_function()
        termination_function = self._create_termination_function()
        
        selection_history_reducer = ChatHistoryTruncationReducer(target_count=5)
        termination_history_reducer = ChatHistoryTruncationReducer(target_count=10)
        
        return AgentGroupChat(
            agents=[
                self.review_coordinator,
                self.tech_reviewer,
                self.relevance_analyst,
                self.implementation_analyst
            ],
            selection_strategy=KernelFunctionSelectionStrategy(
                initial_agent=self.review_coordinator,
                function=selection_function,
                kernel=self.kernel,
                result_parser=lambda result: str(result.value[0]).strip() if result.value else MAIN_REVIEWER_NAME,
                history_variable_name="lastmessage",
                all_history_variable_name="history",
                history_reducer=selection_history_reducer,
            ),
            termination_strategy=KernelFunctionTerminationStrategy(
                agents=[self.review_coordinator],
                function=termination_function,
                kernel=self.kernel,
                result_parser=lambda result: "complete" in result.value[0].content.lower() if result.value and result.value[0].content else False,
                history_variable_name="lastmessage",
                all_history_variable_name="history",
                maximum_iterations=25,
                history_reducer=termination_history_reducer,
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
        
        # Save any existing system messages
        system_messages = [msg for msg in self.chat.history.messages if msg.role == "system"]
        
        # Reset the chat for a new conversation
        await self.chat.reset()
        
        # Restore system messages if any were saved
        if system_messages:
            for system_msg in system_messages:
                self.chat.history.messages.append(system_msg)
            logger.info(f"Restored {len(system_messages)} system message(s) after reset")
        else:
            # If no system messages were saved, add a new one
            self._add_system_message()
        
        # Add the user prompt to the chat
        # NOTE: The initial user prompt doesn't count towards maximum_iterations
        # The first iteration starts when the first agent (Coordinator) responds.
        await self.chat.add_chat_message(message=prompt)
        
        # Invoke the chat and yield responses
        async for response in self.chat.invoke():
            if response is None or not response.name:
                continue
            logger.info(f"Response from {response.name}: {response.content[:50]}...")
            yield response 

    def _add_system_message(self):
        """Add a system message to the chat history to guide the agent conversation."""
        from semantic_kernel.contents.chat_message_content import ChatMessageContent
        from semantic_kernel.contents.utils.author_role import AuthorRole
        
        system_message = ChatMessageContent(
            role=AuthorRole.SYSTEM,
            content="""You are a team of specialized reviewers working together to create a comprehensive, 
            well-structured review. The ReviewCoordinator will guide the process and summarize findings from 
            other specialists. Each specialist should provide thorough analysis in their area of expertise."""
        )
        
        # Add the system message to the chat history directly
        # This bypasses the add_chat_message methods that would previously reject system messages
        self.chat.history.messages.append(system_message)
        
        logger.info("Added system message to chat history") 