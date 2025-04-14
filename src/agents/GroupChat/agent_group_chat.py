"""
Group chat implementation for document review agents using Semantic Kernel's AgentGroupChat.
"""

import asyncio
import logging
from typing import Callable, Optional, Dict

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import (
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelFunctionFromPrompt


from .agent_config import (
    get_initial_prompt_template,
    get_recommendation_prompt_template,
    get_fallback_recommendation_template,
)
from .agent_factory import create_all_agents, create_recommendation_agent
from .message_handler import MessageHandler

# Constants for agent names
LEAD_ADVISOR_NAME = "LeadTechnologyAdvisor"
INNOVATIVE_VISIONARY_NAME = "InnovativeVisionary"
CRITICAL_REVIEWER_NAME = "CriticalReviewer"
BUSINESS_ADVISOR_NAME = "BusinessAdvisor"

# Change these to change which agents lead the discussion and recommendation
DISCUSSION_LEADER = LEAD_ADVISOR_NAME
RECOMMENDATION_LEADER = LEAD_ADVISOR_NAME

logger = logging.getLogger(__name__)


# Helper function to format state information
def format_state_suffix(last_speaker: Optional[str], msg_count: int) -> str:
    """Format the conversation state as a string to include in prompts."""
    return f"""
=== CONVERSATION STATE ===
LAST SPEAKER: {last_speaker or "none"}
MESSAGE COUNT: {msg_count}
========================
"""


class DocumentReviewChat:
    """
    Manages a group chat for document review with multiple agents using Semantic Kernel.

    This class handles the creation and configuration of agents, group chat management,
    and document discussion orchestration.
    """

    def __init__(self, kernel: Optional[Kernel] = None):
        """
        Initialize the document review chat system.

        Args:
            kernel: Optional Kernel instance to use. If not provided, one will be created.
        """
        self.message_handler = MessageHandler()
        self.kernel = kernel if kernel is not None else self._create_kernel()
        self.agents = create_all_agents(self.kernel)

        # Track conversation state
        self.conversation_state = {
            "message_count": 0,
            "last_speaker": None,
        }

        self.group_chat = self._create_group_chat()

        # NEED TO ADD MEMORY HERE
        # Add memory capabilities with just VolatileMemoryStore
        # try:
        #     memory_store = VolatileMemoryStore()
        #     memory_builder = MemoryBuilder()
        #     memory = memory_builder.with_memory_store(memory_store).build()
        #     self.kernel.register_memory(memory)
        #     logger.info("Memory capabilities added to agents")
        # except Exception as e:
        #     logger.warning(f"Could not add memory capabilities: {e}")

    def set_broadcaster(self, broadcaster: Callable) -> None:
        """
        Set the function to broadcast messages to the visualization interface.

        Args:
            broadcaster: A callable function that accepts message dictionaries
        """
        self.message_handler.set_broadcaster(broadcaster)
        logger.info("Visualization broadcaster has been set up for agent messages")

    def _create_kernel(self) -> Kernel:
        """
        Create a Semantic Kernel instance with appropriate chat completion service.

        Returns:
            A configured Semantic Kernel instance

        Note:
            This is a fallback method and should not be called directly.
            Prefer passing a kernel to the constructor instead.
        """
        try:
            from .kernel_provider import KernelProvider

            return KernelProvider.get_kernel()
        except (ImportError, ValueError) as e:
            logger.error(f"Error creating kernel: {e}")
            raise

    def _create_selection_function(self):
        """Create an intelligent agent selection function that chooses the next speaker."""
        agent_names = ", ".join([f"- {name}" for name in self.agents.keys()])

        return KernelFunctionFromPrompt(
            function_name="agent_selection",
            prompt=f"""
You are managing a conversation between different expert agents reviewing a document.
Examine the conversation history to determine which agent should speak next.

Choose from these participants:
{agent_names}

Guidelines:
- NEVER select the same agent to speak twice in a row
- Ensure all agents participate in the discussion
- Select the agent who can contribute most meaningfully to the current discussion point
- The {LEAD_ADVISOR_NAME} should moderate when the discussion needs synthesis or guidance
- After 8-12 total messages, the {LEAD_ADVISOR_NAME} should provide a conclusion

You MUST check the CONVERSATION STATE information to make your decision:

RECENT MESSAGES:
{{$lastmessage}}

SELECTED AGENT (name only, do not include any explanations):
""",
        )

    def _create_termination_function(self):
        """Create a function to determine when the discussion should terminate."""
        return KernelFunctionFromPrompt(
            function_name="discussion_termination",
            prompt="""
Evaluate whether the document discussion has reached a point of completion.
Consider the following criteria:

1. Has each agent (Lead Technology Advisor, Innovative Visionary, Critical Reviewer, Business Advisor) spoken at least once?
2. Has there been meaningful back-and-forth discussion on key points?
3. Has the Lead Technology Advisor provided a summary or concluding remarks?
4. Has the discussion reached at least 6 meaningful total exchanges?

CONVERSATION HISTORY:
{{$lastmessage}}

VERY IMPORTANT INSTRUCTIONS:
- Your answer must start with either "DECISION: continue" or "DECISION: complete"
- Choose "complete" only if criteria 1-3 are met AND the discussion seems to have reached a natural conclusion
- Provide brief reasoning after your decision

DECISION:
""",
        )

    def _create_group_chat(self) -> AgentGroupChat:
        """
        Create the group chat with all agent personas.

        Returns:
            A configured AgentGroupChat instance
        """
        try:
            # Create history reducer to limit context
            history_reducer = ChatHistoryTruncationReducer(target_count=8)

            # Use agents from the agent dictionary
            lead_advisor_agent = self.agents[LEAD_ADVISOR_NAME]

            # Create intelligent selection strategy
            selection_function = self._create_selection_function()
            selection_strategy = KernelFunctionSelectionStrategy(
                initial_agent=lead_advisor_agent,
                function=selection_function,
                kernel=self.kernel,
                result_parser=lambda result: self._parse_agent_selection(result.value[0]) if result.value[0] is not None else LEAD_ADVISOR_NAME,
                history_variable_name="lastmessage",
                history_reducer=history_reducer,
            )

            # Create intelligent termination strategy with stricter limits
            termination_function = self._create_termination_function()
            
            # Define a custom result parser with better logging
            def termination_parser(result):
                result_text = str(result.value[0]).lower() if result.value[0] else ""
                has_complete = "complete" in result_text
                has_continue = "continue" in result_text
                
                logger.info(f"Termination function returned: {result_text[:50]}...")
                logger.info(f"Detected complete={has_complete}, continue={has_continue}")
                
                # Only terminate if explicitly "complete" and not "continue"
                should_terminate = has_complete and not has_continue
                logger.info(f"Termination decision: should_terminate={should_terminate}")
                return should_terminate
            
            termination_strategy = KernelFunctionTerminationStrategy(
                agents=[lead_advisor_agent],
                function=termination_function,
                kernel=self.kernel,
                result_parser=termination_parser,
                history_variable_name="lastmessage",
                maximum_iterations=15,  # Increased from 10 to allow for proper conversation flow
                history_reducer=history_reducer,
            )

            # Create group chat
            return AgentGroupChat(
                agents=list(self.agents.values()),
                selection_strategy=selection_strategy,
                termination_strategy=termination_strategy,
                chat_history=None,
            )
        except Exception as e:
            logger.error(f"Error creating group chat: {e}")
            raise

    async def discuss_document(self, document: str, title: str, rounds: int = 2) -> str:
        """
        Conduct a discussion about the document among the agents.

        Args:
            document: The document text to discuss
            title: The title of the document
            rounds: Number of rounds of discussion (not directly used, controlled by termination strategy)

        Returns:
            A string containing the full discussion transcript

        Raises:
            ValueError: If document or title is empty
        """
        if not document:
            raise ValueError("Document text cannot be empty")

        if not title:
            title = "Untitled Document"

        # Reset group chat if any previous discussions occurred
        await self.group_chat.reset()
        self.message_handler.clear_messages()

        # Reset conversation state
        self.conversation_state = {
            "message_count": 0,
            "last_speaker": None,
        }

        # Start the discussion with context
        initial_prompt = get_initial_prompt_template().format(
            title=title, document=document, lead_advisor=DISCUSSION_LEADER
        )

        # Add initial state information to help with selection
        initial_state = format_state_suffix(
            last_speaker=self.conversation_state["last_speaker"],
            msg_count=self.conversation_state["message_count"],
        )

        # Add state information to the initial prompt
        initial_prompt += initial_state

        # Add the initial prompt to the chat history
        await self.group_chat.add_chat_message(initial_prompt)

        # Log that we're starting the discussion
        logger.info(f"Starting agent discussion for document: {title}")

        # Invoke group chat and process responses
        try:
            # Group chat is invoked, which triggers the agent selection/response cycle
            async for response in self.group_chat.invoke():
                if response and response.role == AuthorRole.ASSISTANT:
                    # Extract agent name and content
                    agent_name = response.name
                    content = response.content

                    logger.info(f"Agent message from {agent_name}: {content[:50]}...")

                    # Update conversation state
                    self.conversation_state["message_count"] += 1
                    self.conversation_state["last_speaker"] = agent_name

                    # Add to our messages list and broadcast
                    # Important: await this to prevent race conditions
                    await self.message_handler.add_message(agent_name, content)

                    # Create updated state information
                    state_info = format_state_suffix(
                        last_speaker=self.conversation_state["last_speaker"],
                        msg_count=self.conversation_state["message_count"],
                    )

                    # Add state information for the next agent selection
                    try:
                        next_agent_prompt = (
                            "\n\n" + state_info +
                            "\n\nContinue the discussion based on the above conversation state. " +
                            f"IMPORTANT: The next agent to speak MUST NOT be {agent_name} (the last speaker). "
                        )
                        logger.info(f"Adding conversation state update after {agent_name}'s message")
                        # Await this to prevent race conditions
                        await self.group_chat.add_chat_message(next_agent_prompt)
                    except Exception as e:
                        logger.warning(f"Could not add state information: {e}")

                    # Small delay between messages for a more natural reading experience
                    await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Error during group chat: {e}")
            logger.exception("Full exception details")

            # Add an error message from the lead advisor
            try:
                await self.message_handler.add_message(
                    LEAD_ADVISOR_NAME,
                    "I apologize, but we've encountered an issue during our discussion. Let's summarize what we've covered so far.",
                )
            except Exception as add_err:
                logger.error(f"Could not add error message: {add_err}")

        # Format the discussion into a transcript
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
            # Extract key insights from the discussion
            discussion_summary = self.message_handler.get_discussion_summary()

            # Create a prompt for the Lead Advisor to generate a recommendation
            recommendation_prompt = get_recommendation_prompt_template().format(
                title=title, discussion_summary=discussion_summary
            )

            # Create a recommendation agent using the factory
            recommendation_agent = create_recommendation_agent(
                self.kernel, RECOMMENDATION_LEADER
            )

            # Create a single-turn chat for the recommendation
            recommendation_chat = AgentGroupChat(agents=[recommendation_agent])

            # Add the recommendation prompt
            await recommendation_chat.add_chat_message(recommendation_prompt)

            # Get the recommendation
            recommendation = ""
            async for response in recommendation_chat.invoke():
                if response and response.role == AuthorRole.ASSISTANT:
                    recommendation = response.content
                    break

            return (
                recommendation
                if recommendation
                else self._get_fallback_recommendation(title)
            )

        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            logger.exception("Full exception details")

            # Return fallback recommendation in case of error
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
    def _parse_agent_selection(self, result):
        """
        Parse the agent selection result and ensure proper agent rotations.
        
        This method enforces simple selection rules to prevent the same agent
        from speaking twice in a row.
        
        Args:
            result: The raw result from the selection function
            
        Returns:
            The name of the agent that should speak next
        """
        # Get the suggested agent from the result
        suggested_agent = str(result).strip()
        result_text = str(result).lower()
        
        # Get the current conversation state
        last_speaker = self.conversation_state["last_speaker"]
        
        # Log the selection suggestion
        logger.info(f"Agent selection suggested: {suggested_agent}, last speaker: {last_speaker}")
        
        # Check for explicit agent references in the selection text
        if "businessadvisor" in result_text or "business advisor" in result_text:
            logger.info("Detected reference to Business Advisor, ensuring they speak next")
            return BUSINESS_ADVISOR_NAME
            
        if "criticalreviewer" in result_text or "critical reviewer" in result_text:
            logger.info("Detected reference to Critical Reviewer, ensuring they speak next")
            return CRITICAL_REVIEWER_NAME
            
        if "innovativevisionary" in result_text or "innovative visionary" in result_text:
            logger.info("Detected reference to Innovative Visionary, ensuring they speak next")
            return INNOVATIVE_VISIONARY_NAME
            
        if "leadtechnologyadvisor" in result_text or "lead technology advisor" in result_text:
            logger.info("Detected reference to Lead Technology Advisor, ensuring they speak next")
            return LEAD_ADVISOR_NAME
        
        # Rule: Never select the same agent twice in a row
        if suggested_agent == last_speaker:
            logger.info(f"Preventing {suggested_agent} from speaking twice in a row")
            
            # Simple rotation if the suggested agent is the same as the last speaker
            if last_speaker == INNOVATIVE_VISIONARY_NAME:
                return CRITICAL_REVIEWER_NAME
            elif last_speaker == CRITICAL_REVIEWER_NAME:
                return BUSINESS_ADVISOR_NAME
            elif last_speaker == BUSINESS_ADVISOR_NAME:
                return LEAD_ADVISOR_NAME
            else:
                return INNOVATIVE_VISIONARY_NAME
                
        # Return the suggested agent if no rules were violated
        return suggested_agent

