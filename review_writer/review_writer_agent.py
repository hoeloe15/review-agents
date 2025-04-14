"""
Review Writer Agent System

This module implements a system of agents for generating comprehensive reviews
based on a given prompt. The system consists of:
1. A main coordinator agent that collects and assembles input from specialized agents
2. A technology reviewer agent that evaluates technical features and market value
3. A relevance & alternatives agent that assesses contextual relevance and alternatives
4. An implementation analyst agent that evaluates implementation aspects
"""

import asyncio
import logging
from typing import List, Dict, Any, AsyncIterable

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.functions import KernelFunctionFromPrompt

from src.utils.kernel_provider import KernelProvider

logger = logging.getLogger(__name__)

# Define agent names
MAIN_REVIEWER_NAME = "ReviewCoordinator"
TECH_REVIEWER_NAME = "TechnologyReviewer"
RELEVANCE_REVIEWER_NAME = "RelevanceAnalyst" 
IMPLEMENTATION_REVIEWER_NAME = "ImplementationAnalyst"

class ReviewWriterSystem:
    """
    A system of agents that collaborate to generate comprehensive reviews.
    
    This system consists of multiple specialized agents that analyze different aspects
    of a product or technology, coordinated by a main reviewer agent that assembles
    their findings into a comprehensive review.
    """
    
    def __init__(self):
        """Initialize the review writer system with specialized agents."""
        # Get a kernel instance from the provider
        self.kernel = KernelProvider.get_kernel()
        
        # Create the specialized agents
        self.tech_reviewer = self._create_tech_reviewer()
        self.relevance_analyst = self._create_relevance_analyst()
        self.implementation_analyst = self._create_implementation_analyst()
        self.review_coordinator = self._create_review_coordinator()
        
        # Create agent group chat with all agents
        self.chat = self._create_group_chat()
    
    def _create_tech_reviewer(self) -> ChatCompletionAgent:
        """Create the technology reviewer agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=TECH_REVIEWER_NAME,
            instructions="""
You are a technology analyst who evaluates products, services, and technologies.
Your responsibility is to provide detailed analysis on:
1. Core technical features and capabilities
2. Competitive positioning in the market
3. Value proposition and unique selling points
4. Technical strengths and limitations

When asked for a review:
- Focus on objective technical assessment
- Highlight stand-out features or innovations
- Discuss market positioning and competition
- Consider both current value and future potential
- Be specific about technical capabilities and limitations

RULES:
- Always support claims with specific technical details
- Maintain technical accuracy in all assessments
- Consider both technical features and market context
- Be balanced in your assessment of strengths and weaknesses
- Avoid marketing language and maintain objective analysis
"""
        )
    
    def _create_relevance_analyst(self) -> ChatCompletionAgent:
        """Create the relevance and alternatives analyst agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=RELEVANCE_REVIEWER_NAME,
            instructions="""
You are an analyst specializing in relevance assessment and alternative solutions.
Your responsibility is to provide detailed analysis on:
1. How relevant the technology/product is for specific use cases
2. Alternative solutions in the marketplace
3. Comparative advantages and disadvantages versus alternatives
4. Specific contexts where this solution excels or falls short

When asked for a review:
- Identify the most appropriate use cases for the technology
- Thoroughly analyze alternative solutions
- Provide a balanced comparison with competitors
- Highlight specific scenarios where this solution is ideal
- Identify contexts where alternatives might be better choices

RULES:
- Always discuss multiple alternatives, not just one
- Be specific about use cases and contexts 
- Provide balanced comparisons with clear criteria
- Consider different user needs and contexts
- Back up claims with specific examples and reasoning
"""
        )
    
    def _create_implementation_analyst(self) -> ChatCompletionAgent:
        """Create the implementation analyst agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=IMPLEMENTATION_REVIEWER_NAME,
            instructions="""
You are an implementation analyst who evaluates practical aspects of technologies and products.
Your responsibility is to provide detailed analysis on:
1. Implementation complexity and requirements
2. Integration capabilities with existing systems
3. Scalability and performance considerations
4. Maintenance and support requirements

When asked for a review:
- Assess technical implementation requirements
- Analyze integration challenges and opportunities
- Evaluate scalability for different usage scenarios
- Consider maintenance burden and long-term support
- Identify potential implementation challenges

RULES:
- Provide practical, implementation-focused perspective
- Consider both technical and organizational factors
- Address scalability concerns for different scales of operation
- Discuss migration and transition strategies when relevant
- Include maintenance and long-term support considerations
"""
        )
    
    def _create_review_coordinator(self) -> ChatCompletionAgent:
        """Create the main review coordinator agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=MAIN_REVIEWER_NAME,
            instructions="""
You are a review coordinator who synthesizes input from multiple specialized analysts.
Your responsibility is to:
1. Ask specific questions to specialized analysts to gather comprehensive information
2. Synthesize input from all analysts into a cohesive review
3. Ensure balanced coverage of technical, relevance, and implementation aspects
4. Create a comprehensive final review that is well-organized and thorough

When coordinating a review:
- Begin by asking each specialist specific questions about their area
- Request clarification when specialist input needs expansion
- Synthesize all perspectives into a comprehensive review
- Ensure the final review addresses technical features, market positioning, alternatives, and implementation considerations

RULES:
- Always gather input from all specialists before synthesizing
- Ensure balanced representation of all perspectives
- Structure the final review in a logical, comprehensive format
- Identify any conflicting perspectives and reconcile them
- Make the final review accessible while maintaining technical accuracy
"""
        )
    
    def _create_selection_function(self) -> KernelFunctionFromPrompt:
        """Create a function to determine which agent should respond next."""
        return KernelFunctionFromPrompt(
            function_name="selection",
            prompt=f"""
Examine the conversation history and determine which agent should respond next.
Choose the most appropriate agent based on the current context and needs.
State only the name of the chosen agent without explanation.

Choose only from these agents:
- {MAIN_REVIEWER_NAME} (Review coordinator who leads the review process)
- {TECH_REVIEWER_NAME} (Specialist in technical features and market positioning)
- {RELEVANCE_REVIEWER_NAME} (Specialist in use cases, relevance, and alternatives)
- {IMPLEMENTATION_REVIEWER_NAME} (Specialist in implementation considerations)

Rules:
- If a user prompt is requesting a review, it is {MAIN_REVIEWER_NAME}'s turn.
- If {MAIN_REVIEWER_NAME} asks a specific question to an agent, select that agent.
- If an agent responds to a question, generally let {MAIN_REVIEWER_NAME} go next to coordinate.
- If reviewing a product, ensure all specialists provide input before final synthesis.

CONVERSATION HISTORY:
{{$history}}

LAST MESSAGE:
{{$lastmessage}}
"""
        )
    
    def _create_termination_function(self) -> KernelFunctionFromPrompt:
        """Create a function to determine when the review is complete."""
        return KernelFunctionFromPrompt(
            function_name="termination",
            prompt=f"""
Determine if the review process is complete based on the conversation history.
A review is complete when all of the following conditions are met:
1. All specialist agents ({TECH_REVIEWER_NAME}, {RELEVANCE_REVIEWER_NAME}, and {IMPLEMENTATION_REVIEWER_NAME}) have provided their analysis
2. The {MAIN_REVIEWER_NAME} has synthesized all input into a comprehensive final review
3. The final review has been presented to the user
4. No follow-up questions remain unanswered

Respond with "complete" if all conditions are met, otherwise respond with "incomplete".

CONVERSATION HISTORY:
{{$history}}

LAST MESSAGE:
{{$lastmessage}}
"""
        )
    
    def _create_group_chat(self) -> AgentGroupChat:
        """Create the agent group chat with all specialized agents."""
        # Create functions for agent selection and termination
        selection_function = self._create_selection_function()
        termination_function = self._create_termination_function()
        
        # Create history reducers
        selection_history_reducer = ChatHistoryTruncationReducer(target_count=5)
        termination_history_reducer = ChatHistoryTruncationReducer(target_count=10)
        
        # Create agent group chat
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
                result_parser=lambda result: "complete" in str(result.value[0]).lower() if result.value else False,
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
        
        # Reset the chat for a new conversation
        await self.chat.reset()
        
        # Add the user prompt to the chat
        await self.chat.add_chat_message(message=prompt)
        
        # Invoke the chat and yield responses
        async for response in self.chat.invoke():
            if response is None or not response.name:
                continue
            logger.info(f"Response from {response.name}: {response.content[:50]}...")
            yield response 