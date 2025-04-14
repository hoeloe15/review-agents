"""
Document review orchestration module.

This module provides the high-level coordination for document review processes,
orchestrating agent discussions and managing the overall review workflow.
"""

import logging
from typing import Dict, Any, Optional

from .document_review_chat import DocumentReviewChat
from .kernel_provider import KernelProvider

logger = logging.getLogger(__name__)


class DocumentReviewOrchestrator:
    """
    Orchestrates the document review process using specialized AI agents.

    This class provides a simplified API for conducting document reviews,
    coordinating the agent group chat, managing visualization, and handling
    the complete review workflow from start to finish.
    """

    def __init__(self, use_existing_kernel: bool = True, moderator_name: Optional[str] = None):
        """
        Initialize the document review orchestrator.

        Args:
            use_existing_kernel: Whether to use an existing kernel instance if available (default: True)
            moderator_name: Optional name of the agent that will lead the discussion
        """
        # Get a kernel instance from the provider
        if not use_existing_kernel:
            self.kernel = KernelProvider.reset_kernel()
        else:
            self.kernel = KernelProvider.get_kernel()

        # Create the document review chat with our kernel
        self.chat = DocumentReviewChat(
            kernel=self.kernel,
            moderator_name=moderator_name
        )
        logger.info("Document review orchestrator initialized with kernel")

    async def evaluate_document(
        self,
        document: str,
        title: Optional[str] = None,
        discussion_focus: Optional[str] = None,
        discussion_rounds: int = 2,
        enable_visualization: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluate a document with a group of AI agents.

        This is the main entry point for document evaluation, providing a simple
        interface to the complete review process.

        Args:
            document: The document text to be evaluated
            title: The title of the document (default: "Document Review")
            discussion_focus: Optional focus topic for the agent discussion
            discussion_rounds: Number of discussion rounds between agents (default: 2)
            enable_visualization: Whether to enable visualization of the agent discussion

        Returns:
            Dictionary with evaluation results containing:
                - title: The document title
                - agent_discussion: Transcript of the agent discussion
                - final_recommendation: The final recommendation
                - error: Error message if an error occurred

        Raises:
            ValueError: If the document is empty
        """
        if not document:
            logger.error("Empty document provided for review")
            raise ValueError("Document for review cannot be empty")

        # Prepare review parameters
        review_params = {
            "document": document,
            "title": title or "Document Review",
            "discussion_rounds": max(1, discussion_rounds),  # Ensure at least 1 round
            "enable_visualization": enable_visualization,
        }

        # Store discussion focus for future use if needed
        if discussion_focus:
            self.chat.state.set_custom_state("discussion_focus", discussion_focus)
            review_params["discussion_focus"] = discussion_focus

        return await self._execute_review_process(review_params)

    async def _execute_review_process(
        self, review_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the document review process with the given parameters.

        Args:
            review_params: Dictionary containing review parameters

        Returns:
            Dictionary with the review results
        """
        document = review_params["document"]
        title = review_params["title"]
        discussion_rounds = review_params["discussion_rounds"]

        logger.info(
            f"Starting review of document: {title} with {discussion_rounds} discussion rounds"
        )

        try:
            # Set up visualization if requested
            if review_params.get("enable_visualization"):
                await self._setup_visualization()

            # Step 1: Conduct the agent discussion
            discussion = await self.chat.discuss_document(
                document=document, title=title, rounds=discussion_rounds
            )

            # Step 2: Generate the final recommendation
            recommendation = await self.chat.get_recommendation(document, title)

            # Step 3: Return the structured results
            return {
                "title": title,
                "agent_discussion": discussion,
                "final_recommendation": recommendation,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error during document review: {e}")
            logger.exception("Full exception details")
            return {
                "title": title,
                "error": f"Error during document review: {str(e)}",
                "agent_discussion": "Discussion could not be completed due to an error.",
                "final_recommendation": "Recommendation could not be generated due to an error.",
                "success": False,
            }

    async def _setup_visualization(self) -> None:
        """
        Set up the visualization broadcaster for the chat.

        This method imports the broadcast_message function from the visualization
        module and sets it as the broadcaster for the chat.
        """
        try:
            # Import the broadcast_message function
            logger.info("Attempting to import visualization broadcast function")
            from visualization.server import broadcast_message

            # Verify the function is callable
            if callable(broadcast_message):
                logger.info("Setting up broadcaster for chat")

                # Set the broadcaster
                self.chat.set_broadcaster(broadcast_message)

                # Test the broadcaster with a system message
                test_message = {
                    "message": "Visualization system initialized",
                    "type": "system",
                }
                logger.info(f"Testing broadcaster with message: {test_message}")
                await broadcast_message(test_message)

                logger.info("Visualization successfully enabled for agent discussion")
            else:
                logger.error(
                    "broadcast_message is not callable - visualization will be disabled"
                )
        except ImportError as e:
            logger.warning(
                f"Visualization module not found: {e}. Visualization will be disabled."
            )
        except Exception as e:
            logger.error(f"Error setting up visualization: {e}")
            logger.exception("Full exception details")

    def reset(self) -> None:
        """
        Reset the orchestrator state.

        This method resets both the kernel and chat states, useful for
        starting a completely fresh document review.
        """
        self.kernel = KernelProvider.reset_kernel()
        self.chat = DocumentReviewChat(kernel=self.kernel)
        logger.info("Document review orchestrator has been reset")
