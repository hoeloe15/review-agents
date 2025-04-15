"""
Review System - Main orchestrator for review generation

This module provides the ReviewSystem class that coordinates specialized agents
to generate comprehensive reviews.
"""

import logging
import re
from typing import AsyncGenerator, List, Dict, Any, Tuple

from semantic_kernel.agents import ChatCompletionAgent
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
        """Initialize the review system with specialized agents and persistent chat histories."""
        # Get a kernel instance from the provider
        self.kernel = KernelProvider.get_kernel()
        
        # Create persistent chat histories for each agent
        self.coordinator_history = ChatHistory()
        self.tech_reviewer_history = ChatHistory()
        self.relevance_analyst_history = ChatHistory()
        self.implementation_analyst_history = ChatHistory()
        
        # Master history to track overall conversation
        self.master_history = ChatHistory()
        
        # Create the specialized agents
        self.tech_reviewer = ChatCompletionAgent(
            kernel=self.kernel,
            name=TECH_REVIEWER_NAME,
            instructions=TECH_REVIEWER_PROMPT
        )
        
        self.relevance_analyst = ChatCompletionAgent(
            kernel=self.kernel,
            name=RELEVANCE_REVIEWER_NAME,
            instructions=RELEVANCE_ANALYST_PROMPT
        )
        
        self.implementation_analyst = ChatCompletionAgent(
            kernel=self.kernel,
            name=IMPLEMENTATION_REVIEWER_NAME,
            instructions=IMPLEMENTATION_ANALYST_PROMPT
        )
        
        self.review_coordinator = ChatCompletionAgent(
            kernel=self.kernel,
            name=MAIN_REVIEWER_NAME,
            instructions=COORDINATOR_PROMPT
        )
    
    async def generate_review_stream(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a comprehensive review and stream each message as it's generated.
        
        Args:
            prompt: The topic to generate a review for
            
        Yields:
            Dictionary with agent information and message content
        """
        logger.info(f"Starting review generation for: {prompt}")
        
        # Add user request to master history
        user_message = f"Please generate a comprehensive review about: {prompt}"
        self.master_history.add_user_message(user_message)
        
        # Yield the user message first
        yield {
            "agent_name": "User",
            "content": user_message,
            "turn": 0
        }
        
        # -- STEP 1: Coordinator creates a plan --
        yield {
            "agent_name": MAIN_REVIEWER_NAME,
            "content": None,  # No content yet
            "turn": 1,
            "status": "thinking"
        }
        
        # Craft a very explicit instruction with the review topic clearly highlighted
        coordinator_prompt = (
            f"REVIEW TOPIC: \"{prompt}\"\n\n"
            f"You are tasked with creating a comprehensive review of {prompt}. "
            f"First, develop a plan by formulating specific questions for three specialist agents who will help with different aspects of the review:\n\n"
            f"1. {TECH_REVIEWER_NAME} - This specialist analyzes technical features, capabilities, and technical strengths/weaknesses\n"
            f"2. {RELEVANCE_REVIEWER_NAME} - This specialist evaluates use cases, alternatives, and comparative advantages\n"
            f"3. {IMPLEMENTATION_REVIEWER_NAME} - This specialist assesses implementation requirements, integration, scalability, and maintenance\n\n"
            f"For each specialist, create 2-3 specific questions about {prompt} related to their expertise area.\n\n"
            f"Format your questions like this:\n"
            f"**{TECH_REVIEWER_NAME}**: [Your first technical question about {prompt}]\n"
            f"**{TECH_REVIEWER_NAME}**: [Your second technical question about {prompt}]\n"
            f"**{RELEVANCE_REVIEWER_NAME}**: [Your first relevance question about {prompt}]\n"
            f"And so on...\n\n"
            f"Be specific and focus exclusively on {prompt}."
        )
        
        # Reset coordinator history for a fresh start
        self.coordinator_history = ChatHistory()
        self.coordinator_history.add_user_message(coordinator_prompt)
        
        # Add to master history as well
        self.master_history.add_user_message(
            f"[System to {MAIN_REVIEWER_NAME}]: Requesting review plan for '{prompt}'"
        )
        
        # Get the coordinator's plan
        coord_plan = ""
        async for chunk in self.review_coordinator.invoke(chat_history=self.coordinator_history):
            if isinstance(chunk, str):
                coord_plan += chunk
            elif hasattr(chunk, 'content'):
                if isinstance(chunk.content, str):
                    coord_plan += chunk.content
                else:
                    coord_plan += str(chunk.content)
        
        # Add coordinator's response to its history and master history
        self.coordinator_history.add_assistant_message(coord_plan)
        self.master_history.add_assistant_message(
            f"[{MAIN_REVIEWER_NAME}]: Plan created for '{prompt}'"
        )
        
        logger.info(f"Coordinator plan created for '{prompt}'")
        
        # Yield the coordinator's plan
        yield {
            "agent_name": MAIN_REVIEWER_NAME,
            "content": coord_plan,
            "turn": 1,
            "status": "complete"
        }
        
        # -- STEP 2: Extract questions and get specialist responses --
        specialist_responses = {}
        
        # Extract questions with improved logging
        questions_by_agent = self._extract_questions(coord_plan)
        logger.info(f"Extracted questions for '{prompt}': {questions_by_agent}")
        
        # Fall back to default questions if extraction failed
        if all(len(questions) == 0 for questions in questions_by_agent.values()):
            logger.warning(f"Question extraction failed for '{prompt}', using default questions")
            questions_by_agent = self._create_default_questions(prompt)
        
        turn_counter = 2
        for agent_name, questions in questions_by_agent.items():
            if not questions:
                logger.warning(f"No questions for {agent_name}, skipping")
                continue
                
            logger.info(f"Processing questions for {agent_name} about '{prompt}'")
                
            # Determine which agent and history to use
            if agent_name == TECH_REVIEWER_NAME:
                agent = self.tech_reviewer
                agent_history = self.tech_reviewer_history
            elif agent_name == RELEVANCE_REVIEWER_NAME:
                agent = self.relevance_analyst
                agent_history = self.relevance_analyst_history
            elif agent_name == IMPLEMENTATION_REVIEWER_NAME:
                agent = self.implementation_analyst
                agent_history = self.implementation_analyst_history
            else:
                logger.warning(f"Unknown agent name: {agent_name}")
                continue
            
            # Yield the agent thinking event
            yield {
                "agent_name": agent_name,
                "content": None,
                "turn": turn_counter,
                "status": "thinking"
            }
            
            # Create a very explicit message with the topic clearly highlighted
            specialist_prompt = (
                f"REVIEW TOPIC: \"{prompt}\"\n\n"
                f"I need your expertise as the {agent_name} to help create a comprehensive review of {prompt}. "
                f"Based on your specialized knowledge, please answer the following specific questions about {prompt}:\n\n"
            )
            
            # Add each question to the prompt with clear numbering
            for i, q in enumerate(questions, 1):
                specialist_prompt += f"Question {i}: {q}\n\n"
            
            specialist_prompt += (
                f"Please provide detailed, informative answers about {prompt} based on your expertise area. "
                f"Your analysis will be combined with other specialists to create a comprehensive review."
            )
            
            # Reset specialist history for a fresh start
            if agent_name == TECH_REVIEWER_NAME:
                self.tech_reviewer_history = ChatHistory()
                agent_history = self.tech_reviewer_history
            elif agent_name == RELEVANCE_REVIEWER_NAME:
                self.relevance_analyst_history = ChatHistory()
                agent_history = self.relevance_analyst_history
            elif agent_name == IMPLEMENTATION_REVIEWER_NAME:
                self.implementation_analyst_history = ChatHistory()
                agent_history = self.implementation_analyst_history
            
            # Add the request to specialist's history
            agent_history.add_user_message(specialist_prompt)
            
            # Add to master history as well
            self.master_history.add_user_message(
                f"[System to {agent_name}]: Questions about '{prompt}'"
            )
            
            # Get the agent's response
            response = ""
            async for chunk in agent.invoke(chat_history=agent_history):
                if isinstance(chunk, str):
                    response += chunk
                elif hasattr(chunk, 'content'):
                    if isinstance(chunk.content, str):
                        response += chunk.content
                    else:
                        response += str(chunk.content)
            
            # Add response to agent's history and master history
            agent_history.add_assistant_message(response)
            self.master_history.add_assistant_message(
                f"[{agent_name}]: Response about '{prompt}'"
            )
            
            logger.info(f"Received response from {agent_name} about '{prompt}'")
            
            # Store the response
            specialist_responses[agent_name] = response
            
            # Yield the agent's response
            yield {
                "agent_name": agent_name,
                "content": response,
                "turn": turn_counter,
                "status": "complete"
            }
            
            turn_counter += 1
        
        # -- STEP 3: Coordinator synthesizes the final review --
        yield {
            "agent_name": MAIN_REVIEWER_NAME,
            "content": None,
            "turn": turn_counter,
            "status": "thinking"
        }
        
        # Create a context-rich synthesis prompt with the topic clearly highlighted
        synthesis_prompt = (
            f"REVIEW TOPIC: \"{prompt}\"\n\n"
            f"You have received responses from specialist agents about {prompt}. "
            f"Your task is to synthesize their insights into a comprehensive, well-structured review.\n\n"
            f"Below are the specialist responses about {prompt}:\n\n"
        )
        
        # Add each specialist's response with clear labeling
        for agent_name, response in specialist_responses.items():
            synthesis_prompt += f"======= {agent_name}'s Analysis of {prompt} =======\n\n{response}\n\n"
        
        # Add clear instructions about using the plugin
        synthesis_prompt += (
            f"FINAL TASK:\n"
            f"Create a comprehensive review of {prompt} by synthesizing the above specialist analyses. "
            f"Use the Reviewer.synthesize_review function with these exact parameters:\n\n"
            f"tech_review: The technical assessment from {TECH_REVIEWER_NAME}\n"
            f"relevance_review: The relevance analysis from {RELEVANCE_REVIEWER_NAME}\n"
            f"implementation_review: The implementation details from {IMPLEMENTATION_REVIEWER_NAME}\n"
            f"product_name: \"{prompt}\"\n"
            f"summary: A concise executive summary of the key findings\n\n"
            f"This function will format your review with appropriate sections."
        )
        
        # Reset coordinator history for synthesis
        self.coordinator_history = ChatHistory()
        self.coordinator_history.add_user_message(synthesis_prompt)
        
        # Add to master history
        self.master_history.add_user_message(
            f"[System to {MAIN_REVIEWER_NAME}]: Requesting synthesis for '{prompt}'"
        )
        
        logger.info(f"Requesting final synthesis about '{prompt}'")
        
        # Get the final review
        final_review = ""
        async for chunk in self.review_coordinator.invoke(chat_history=self.coordinator_history):
            if isinstance(chunk, str):
                final_review += chunk
            elif hasattr(chunk, 'content'):
                if isinstance(chunk.content, str):
                    final_review += chunk.content
                else:
                    final_review += str(chunk.content)
        
        # Add final review to coordinator's history and master history
        self.coordinator_history.add_assistant_message(final_review)
        self.master_history.add_assistant_message(
            f"[{MAIN_REVIEWER_NAME}]: Final Review of '{prompt}' completed"
        )
        
        logger.info(f"Final review of '{prompt}' generated")
        
        # Yield the final review
        yield {
            "agent_name": MAIN_REVIEWER_NAME,
            "content": final_review,
            "turn": turn_counter,
            "status": "complete"
        }
        
        # Yield completion notification
        yield {
            "agent_name": "System",
            "content": f"Review of '{prompt}' complete",
            "turn": turn_counter + 1,
            "status": "end"
        }
    
    def _extract_questions(self, coordinator_plan: str) -> Dict[str, List[str]]:
        """
        Extract questions for each specialist agent from the coordinator's plan.
        
        Args:
            coordinator_plan: The plan generated by the coordinator
            
        Returns:
            Dict mapping agent names to lists of questions
        """
        questions = {
            TECH_REVIEWER_NAME: [],
            RELEVANCE_REVIEWER_NAME: [],
            IMPLEMENTATION_REVIEWER_NAME: []
        }
        
        # Log the coordinator plan for debugging
        logger.debug(f"Extracting questions from coordinator plan")
        
        # Try multiple pattern formats to increase robustness
        patterns = [
            # Bold markdown: **AgentName**:
            (r"\*\*({})\*\*:\s*(.*?)(?=\n\s*\*\*|\Z)", "Bold markdown"),
            # Regular format: AgentName:
            (r"({})[:][ ]+(.*?)(?=\n\s*[A-Za-z]|$)", "Regular format"),
            # Numbered format: 1. AgentName:
            (r"\d+\.\s*({})[:][ ]+(.*?)(?=\n\s*\d+\.|\Z)", "Numbered format")
        ]
        
        # Try each pattern format
        for pattern_template, pattern_name in patterns:
            logger.debug(f"Trying extraction with {pattern_name}")
            any_questions_found = False
            
            for agent_name in questions.keys():
                # Create pattern for this specific agent
                pattern = pattern_template.format(agent_name)
                matches = re.finditer(pattern, coordinator_plan, re.DOTALL)
                
                for match in matches:
                    if pattern_name == "Bold markdown" or pattern_name == "Regular format":
                        question_text = match.group(2).strip()
                    else:  # Numbered format
                        question_text = match.group(2).strip()
                    
                    if question_text:
                        questions[agent_name].append(question_text)
                        any_questions_found = True
                        logger.debug(f"Found question for {agent_name}: {question_text}")
            
            # If we found any questions with this pattern, stop trying other patterns
            if any_questions_found:
                logger.info(f"Successfully extracted questions using {pattern_name}")
                break
        
        # Fallback to line-by-line parsing if no questions found
        if all(len(qs) == 0 for qs in questions.values()):
            logger.warning("Regex extraction failed, falling back to line-by-line parsing")
            current_agent = None
            for line in coordinator_plan.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this line starts with an agent name
                for agent in questions.keys():
                    if f"**{agent}**:" in line or f"{agent}:" in line:
                        current_agent = agent
                        # Extract the question part after the agent name
                        question = re.sub(r".*?\*\*?{}(\*\*)?:".format(agent), "", line).strip()
                        if question:
                            questions[current_agent].append(question)
                            logger.debug(f"Line parsing found question for {agent}: {question}")
                        break
                else:
                    # If no agent mentioned but we have a current agent, treat as continuation
                    if current_agent and not any(f"{agent}" in line for agent in questions.keys()):
                        if questions[current_agent]:
                            questions[current_agent][-1] += f" {line}"
                        elif line:  # If somehow we have a current agent but no questions yet
                            questions[current_agent].append(line)
        
        # Log the results
        for agent, agent_questions in questions.items():
            logger.info(f"Extracted {len(agent_questions)} questions for {agent}")
        
        return questions
    
    def _create_default_questions(self, topic: str) -> Dict[str, List[str]]:
        """
        Create default questions for each specialist when extraction fails.
        
        Args:
            topic: The review topic
            
        Returns:
            Dict mapping agent names to lists of default questions
        """
        logger.info(f"Creating default questions for topic: {topic}")
        
        return {
            TECH_REVIEWER_NAME: [
                f"What are the key technical features and capabilities of {topic}?",
                f"How does {topic} compare technically to competitors in the market?",
                f"What are the technical strengths and limitations of {topic}?"
            ],
            RELEVANCE_REVIEWER_NAME: [
                f"What are the primary use cases for {topic}?",
                f"What alternatives exist to {topic} and how do they compare?",
                f"For which contexts and users is {topic} most relevant and appropriate?"
            ],
            IMPLEMENTATION_REVIEWER_NAME: [
                f"What are the implementation requirements and complexity considerations for {topic}?",
                f"How well does {topic} integrate with existing systems and technologies?",
                f"What are the scalability and maintenance aspects of {topic}?"
            ]
        }

