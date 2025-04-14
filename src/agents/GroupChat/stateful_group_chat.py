"""
Stateful group chat implementation extending Semantic Kernel's AgentGroupChat.

This module provides a stateful extension to AgentGroupChat that maintains conversation
state, enabling better agent selection and more coherent multi-agent discussions.
"""

import asyncio
import logging
from typing import List, Callable, Dict, Optional, Any, Union

from semantic_kernel import Kernel
from semantic_kernel.agents import Agent, AgentGroupChat
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy, KernelFunctionTerminationStrategy
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelFunctionFromPrompt

from .conversation_state import ConversationState
from .message_handler import MessageHandler

logger = logging.getLogger(__name__)


class StatefulGroupChat:
    """
    Stateful group chat for multi-agent conversations with state tracking.
    
    This class extends the basic functionality of AgentGroupChat to include
    conversation state tracking and management, enabling more coherent and
    controllable agent interactions.
    """
    
    def __init__(
        self,
        agents: List[Agent],
        kernel: Kernel,
        initial_agent_name: Optional[str] = None,
        state: Optional[ConversationState] = None,
        message_handler: Optional[MessageHandler] = None,
        history_truncation: int = 8,
        max_iterations: int = 15
    ):
        """
        Initialize the stateful group chat.
        
        Args:
            agents: List of agent instances to participate in the chat
            kernel: Semantic Kernel instance
            initial_agent_name: Name of the agent that should speak first
            state: Optional ConversationState instance (will create one if not provided)
            message_handler: Optional MessageHandler for broadcasting messages
            history_truncation: Number of messages to keep in context
            max_iterations: Maximum iterations before forced termination
        """
        self.agents = agents
        self.kernel = kernel
        self.message_handler = message_handler or MessageHandler()
        
        # Create an agent name to agent mapping
        self.agent_map = {agent.name: agent for agent in agents}
        self.agent_names = list(self.agent_map.keys())
        
        # Set initial agent if provided, otherwise use the first agent
        if initial_agent_name and initial_agent_name in self.agent_map:
            self.initial_agent = self.agent_map[initial_agent_name]
        else:
            self.initial_agent = agents[0]
            
        # Set up conversation state
        self.state = state or ConversationState()
        
        # Create history reducer
        self.history_reducer = ChatHistoryTruncationReducer(target_count=history_truncation)
        
        # Create the underlying group chat
        self.group_chat = self._create_group_chat(max_iterations)
        
    def _create_group_chat(self, max_iterations: int) -> AgentGroupChat:
        """
        Create the underlying AgentGroupChat with appropriate selection and termination strategies.
        
        Args:
            max_iterations: Maximum number of iterations before forced termination
            
        Returns:
            Configured AgentGroupChat instance
        """
        # Create agent selection strategy
        selection_function = self._create_selection_function()
        selection_strategy = KernelFunctionSelectionStrategy(
            initial_agent=self.initial_agent,
            function=selection_function,
            kernel=self.kernel,
            history_variable_name="lastmessage",
            history_reducer=self.history_reducer,
        )
        
        # Create termination strategy
        termination_function = self._create_termination_function()
        termination_strategy = KernelFunctionTerminationStrategy(
            agents=[self.initial_agent],  # Usually we want the moderator to decide when to end
            function=termination_function,
            kernel=self.kernel,
            history_variable_name="lastmessage",
            maximum_iterations=max_iterations,
            history_reducer=self.history_reducer,
        )
        
        # Create and return the group chat
        return AgentGroupChat(
            agents=self.agents,
            selection_strategy=selection_strategy,
            termination_strategy=termination_strategy,
            chat_history=None,  # Start with empty history
        )
    
    def _create_selection_function(self) -> KernelFunctionFromPrompt:
        """
        Create a function to intelligently select the next agent to speak.
        
        Returns:
            A KernelFunction for agent selection
        """
        # Get a formatted list of agent names
        agent_names_list = ", ".join([f"- {name}" for name in self.agent_names])
        
        return KernelFunctionFromPrompt(
            function_name="agent_selection",
            prompt=f"""
You are managing a conversation between different expert agents.
Examine the conversation history to determine which agent should speak next.

Choose from these participants:
{agent_names_list}

Guidelines:
- NEVER select the same agent to speak twice in a row
- Ensure all agents participate in the discussion
- Select the agent who can contribute most meaningfully to the current discussion point
- After 8-10 total messages, consider wrapping up the discussion

You MUST check the CONVERSATION STATE information to make your decision:

RECENT MESSAGES:
{{$lastmessage}}

SELECTED AGENT (name only, do not include any explanations):
""",
        )
    
    def _create_termination_function(self) -> KernelFunctionFromPrompt:
        """
        Create a function to determine when the discussion should end.
        
        Returns:
            A KernelFunction for determining termination
        """
        return KernelFunctionFromPrompt(
            function_name="discussion_termination",
            prompt=f"""
Evaluate whether the multi-agent discussion has reached a point of completion.
Consider these criteria:

1. Have all agents ({", ".join(self.agent_names)}) spoken at least once?
2. Has there been meaningful back-and-forth discussion on key points?
3. Has the discussion reached a natural conclusion?
4. Have at least 6-8 meaningful exchanges occurred?

Look at the CONVERSATION STATE to help make your decision.

CONVERSATION HISTORY:
{{$lastmessage}}

DECISION: Your answer must start with either "DECISION: continue" or "DECISION: complete"
- Choose "continue" if more meaningful discussion is likely
- Choose "complete" if criteria 1-3 are met

DECISION:
""",
        )
    
    def set_broadcaster(self, broadcaster: Callable) -> None:
        """
        Set a function to broadcast messages to external systems.
        
        Args:
            broadcaster: Callable that accepts message dictionaries
        """
        self.message_handler.set_broadcaster(broadcaster)
    
    async def add_message(self, message: str) -> None:
        """
        Add a message to the chat history.
        
        Args:
            message: The message text to add
        """
        await self.group_chat.add_chat_message(message)
    
    async def reset(self) -> None:
        """Reset the group chat and conversation state."""
        await self.group_chat.reset()
        self.message_handler.clear_messages()
        self.state.reset()
        logger.info("Stateful group chat has been reset")
    
    async def invoke(self, initial_message: Optional[str] = None, include_state: bool = True):
        """
        Start the group chat conversation and yield responses.
        
        Args:
            initial_message: Optional message to start the conversation
            include_state: Whether to include state information in prompts
            
        Yields:
            Agent responses as they occur
        """
        # Add initial message if provided
        if initial_message:
            # Add initial state info if requested
            if include_state:
                initial_message += f"\n\n{self.state.format_as_prompt()}"
            
            await self.add_message(initial_message)
            logger.info("Added initial message to group chat")
        
        # Process agent responses
        try:
            async for response in self.group_chat.invoke():
                if response and response.role == AuthorRole.ASSISTANT:
                    agent_name = response.name
                    content = response.content
                    
                    logger.info(f"Agent message from {agent_name}: {content[:50]}...")
                    
                    # Update conversation state
                    self.state.update_after_message(agent_name)
                    
                    # Add to message handler and broadcast
                    await self.message_handler.add_message(agent_name, content)
                    
                    # Add updated state information for next agent selection
                    if include_state:
                        state_info = self.state.format_as_prompt()
                        next_prompt = (
                            f"\n\n{state_info}\n\n"
                            f"Continue the discussion. The next speaker should NOT be {agent_name}."
                        )
                        await self.add_message(next_prompt)
                    
                    # Small delay for more natural conversation flow
                    await asyncio.sleep(0.5)
                    
                    # Yield the response
                    yield response
        
        except Exception as e:
            logger.error(f"Error during group chat: {e}")
            logger.exception("Full exception details")
            
            # If we have an initial agent, add an error message
            if self.initial_agent:
                try:
                    error_message = (
                        "I apologize, but we've encountered an issue during our discussion. "
                        "Let's summarize what we've covered so far."
                    )
                    await self.message_handler.add_message(self.initial_agent.name, error_message)
                except Exception as add_err:
                    logger.error(f"Could not add error message: {add_err}")
    
    def get_transcript(self, title: str = "Discussion") -> str:
        """
        Get a formatted transcript of the conversation.
        
        Args:
            title: Optional title for the transcript
            
        Returns:
            Formatted transcript string
        """
        return self.message_handler.format_transcript(title) 