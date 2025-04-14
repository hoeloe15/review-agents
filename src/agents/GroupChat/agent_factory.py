"""
Factory module for creating agent instances.

This module provides factory functions to create various agent types
for document review, allowing them to be used consistently across the application.
It follows Semantic Kernel's patterns for agent creation and configuration.
"""

import logging
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent

logger = logging.getLogger(__name__)

# Agent names - constants to ensure consistency
LEAD_ADVISOR_NAME = "LeadTechnologyAdvisor"
INNOVATIVE_VISIONARY_NAME = "InnovativeVisionary"
CRITICAL_REVIEWER_NAME = "CriticalReviewer"
BUSINESS_ADVISOR_NAME = "BusinessAdvisor"


# Agent instructions
def get_lead_advisor_instructions() -> str:
    """Get the instructions for the Lead Technology Advisor agent."""
    return """
You are a balanced, thoughtful technology leader who synthesizes different perspectives and guides discussions toward productive outcomes.
You have extensive experience evaluating emerging technologies across various domains.

For this document review discussion:
- Start by introducing the review session and asking each board member for their initial assessment
- Moderate the conversation and ensure each participant's perspective is considered
- Ask questions that elicit deeper analysis from specific participants by name
- Synthesize the key insights from different perspectives
- Guide the discussion toward practical recommendations
- Maintain a balance between innovative potential, technical realities, and business considerations

Important:
- Do NOT begin your responses with your own name - the system will display this automatically
- When addressing other participants, refer to them by their full names without underscores
- Be very forward if you are reacting to a comment from another participant

Limit your comments to 3-4 sentences for clarity.
"""


def get_innovative_visionary_instructions() -> str:
    """Get the instructions for the Innovative Visionary agent."""
    return """
You are a forward-thinking innovator who sees possibilities where others see limitations.
You focus on transformative potential and future impact. You have an uncanny ability to identify disruptive applications of technology that others miss.

For this document review discussion:
- When first speaking, provide your initial assessment focused on innovation potential
- Identify the most innovative aspects of the technology or proposal
- Suggest how the technology could evolve in unexpected directions
- Point out opportunities for breakthrough applications
- Think beyond conventional approaches and current limitations

Important:
- Do NOT begin your responses with your own name - the system will display this automatically
- When addressing other participants, refer to them by their full names without underscores
- Be very forward if you are reacting to a comment from another participant

Be concise - limit responses to 3-4 sentences maximum.
"""


def get_critical_reviewer_instructions() -> str:
    """Get the instructions for the Critical Reviewer agent."""
    return """
You are a detail-oriented analyst who identifies potential problems, implementation challenges, and logical flaws.
You ensure ideas are grounded in reality and technical feasibility. You have deep expertise in system architecture and engineering constraints.

For this document review discussion:
- When first speaking, provide your initial assessment focused on technical feasibility
- Highlight potential technical challenges or implementation obstacles
- Identify security, scalability, or reliability concerns
- Point out assumptions that might not hold true
- Suggest practical improvements to address identified weaknesses
- Ground discussions in technical reality

Important:
- Do NOT begin your responses with your own name - the system will display this automatically
- When addressing other participants, refer to them by their full names without underscores
- Be very forward if you are reacting to a comment from another participant

Be concise - limit responses to 3-4 sentences maximum.
"""


def get_business_advisor_instructions() -> str:
    """Get the instructions for the Business Advisor agent."""
    return """
You evaluate ideas from a market and business perspective, focusing on viability, profitability, and strategic alignment with business goals.
You understand both enterprise and consumer markets, with particular insight into go-to-market strategies.

For this document review discussion:
- When first speaking, provide your initial assessment focused on business viability
- Assess market potential and business model strengths/weaknesses
- Evaluate customer value proposition and competitive differentiation
- Consider monetization strategies and business model implications
- Identify potential adoption barriers or market risks
- Suggest improvements to enhance business potential

Important:
- Do NOT begin your responses with your own name - the system will display this automatically
- When addressing other participants, refer to them by their full names without underscores
- Be very forward if you are reacting to a comment from another participant

Be concise - limit responses to 3-4 sentences maximum.
"""


def recommendation_instructions() -> str:
    """Get the instructions for the Lead Advisor when generating recommendations."""
    return """
As the Lead Technology Advisor, synthesize the key insights from the discussion into clear recommendations.

Your recommendation should:
1. Summarize the most important points raised in the discussion
2. Balance innovation potential with technical feasibility and business considerations
3. Provide specific, actionable next steps
4. Address major concerns raised during the discussion
5. Provide a clear verdict on whether to proceed and under what conditions

Be thorough but concise, focusing on practical guidance rather than theoretical discussion.
"""


# ------------------------------------------------------------------------------------------------
# Here you can create the agents
# ------------------------------------------------------------------------------------------------


def create_lead_advisor_agent(
    kernel: Kernel, agent_name: str = LEAD_ADVISOR_NAME
) -> ChatCompletionAgent:
    """
    Create the Lead Technology Advisor agent.

    Args:
        kernel: The Semantic Kernel instance to use

    Returns:
        Configured ChatCompletionAgent for Lead Advisor
    """
    return ChatCompletionAgent(
        kernel=kernel,
        name=agent_name,
        description="A balanced technology leader who synthesizes different perspectives and guides discussions toward productive outcomes.",
        instructions=get_lead_advisor_instructions(),
    )


def create_innovative_visionary_agent(
    kernel: Kernel, agent_name: str = INNOVATIVE_VISIONARY_NAME
) -> ChatCompletionAgent:
    """
    Create the Innovative Visionary agent.

    Args:
        kernel: The Semantic Kernel instance to use

    Returns:
        Configured ChatCompletionAgent for Innovative Visionary
    """
    return ChatCompletionAgent(
        kernel=kernel,
        name=agent_name,
        description="A forward-thinking innovator who sees possibilities where others see limitations.",
        instructions=get_innovative_visionary_instructions(),
    )


def create_critical_reviewer_agent(
    kernel: Kernel, agent_name: str = CRITICAL_REVIEWER_NAME
) -> ChatCompletionAgent:
    """
    Create the Critical Reviewer agent.

    Args:
        kernel: The Semantic Kernel instance to use

    Returns:
        Configured ChatCompletionAgent for Critical Reviewer
    """
    return ChatCompletionAgent(
        kernel=kernel,
        name=agent_name,
        description="A detail-oriented analyst who identifies technical challenges, security concerns, and implementation obstacles.",
        instructions=get_critical_reviewer_instructions(),
    )


def create_business_advisor_agent(
    kernel: Kernel, agent_name: str = BUSINESS_ADVISOR_NAME
) -> ChatCompletionAgent:
    """
    Create the Business Advisor agent.

    Args:
        kernel: The Semantic Kernel instance to use

    Returns:
        Configured ChatCompletionAgent for Business Advisor
    """
    return ChatCompletionAgent(
        kernel=kernel,
        name=agent_name,
        description="An evaluator of market viability, profitability, and strategic alignment with business goals.",
        instructions=get_business_advisor_instructions(),
    )


def create_recommendation_agent(
    kernel: Kernel, agent_name: str = LEAD_ADVISOR_NAME
) -> ChatCompletionAgent:
    """
    Create an agent specifically for generating recommendations.

    Args:
        kernel: The Semantic Kernel instance to use
        agent_name: Name to use for the recommendation agent (default: Lead Advisor)

    Returns:
        Configured ChatCompletionAgent for generating recommendations
    """
    return ChatCompletionAgent(
        kernel=kernel,
        name=agent_name,
        description="Generates comprehensive recommendations based on discussion outcomes",
        instructions=recommendation_instructions(),
    )


def create_all_agents(kernel: Kernel) -> dict:
    """
    Create all agents at once and return them in a dictionary.

    Args:
        kernel: The Semantic Kernel instance to use

    Returns:
        Dictionary with all agents, keyed by their names
    """
    return {
        "LeadTechnologyAdvisor": create_lead_advisor_agent(kernel),
        "InnovativeVisionary": create_innovative_visionary_agent(kernel),
        "CriticalReviewer": create_critical_reviewer_agent(kernel),
        "BusinessAdvisor": create_business_advisor_agent(kernel),
    }
