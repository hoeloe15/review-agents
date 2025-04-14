"""
Review Plugin - Functions for review generation and analysis

This module provides specialized plugin functions for the review system,
allowing agents to perform tasks related to review generation and formatting.
"""

import logging
import typing as t  # Add typing import

from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)

class ReviewPlugin:
    """
    Plugin providing functions for review generation and management.
    
    This plugin provides specialized functions for the review coordinator agent
    to organize and synthesize feedback from other specialist agents.
    """

    @kernel_function(
        description="Format and synthesize a comprehensive review from multiple inputs",
        name="synthesize_review"
    )
    async def synthesize_review(
        self, 
        tech_review: t.Annotated[str, "Detailed technical assessment from the TechnologyReviewer"],
        relevance_review: t.Annotated[str, "Analysis of relevance and alternatives from the RelevanceAnalyst"],
        implementation_review: t.Annotated[str, "Analysis of implementation details from the ImplementationAnalyst"],
        product_name: t.Annotated[str, "The name of the product/technology being reviewed"],
        summary: t.Annotated[str, "A concise executive summary of the review findings"]
    ) -> str:
        """
        Format and synthesize a comprehensive review from multiple inputs.
        
        Args:
            tech_review: Detailed technical assessment.
            relevance_review: Analysis of relevance and alternatives.
            implementation_review: Analysis of implementation details.
            product_name: Name of the product/technology.
            summary: Executive summary.
                    
        Returns:
            A formatted comprehensive review that synthesizes all inputs.
        """
        # Create structured review
        review = f"""
# Comprehensive Review: {product_name}

## Executive Summary
{summary}

## Technical Assessment
{tech_review}

## Relevance and Alternatives Analysis
{relevance_review}

## Implementation Considerations
{implementation_review}

## Conclusion
This review synthesizes analysis from multiple specialized perspectives to provide
a comprehensive assessment of {product_name}. The analysis covers technical features, 
market positioning, relevance, alternatives, and implementation considerations.
"""
        
        logger.info(f"Synthesized comprehensive review for {product_name}")
        return review

    @kernel_function(
        description="Extract key takeaways from a review",
        name="extract_key_takeaways"
    )
    async def extract_key_takeaways(
        self, 
        review: t.Annotated[str, "The full text of the comprehensive review to extract takeaways from"]
    ) -> str:
        """
        Extract and format key takeaways from a comprehensive review.
        
        Args:
            review: The comprehensive review text.
                    
        Returns:
            A formatted instruction prompt for the LLM to extract key takeaways.
        """
        # Format for extraction instruction
        instruction = f"""
Extract 3-5 key takeaways from the following review. 
Format them as a bullet-point list.

REVIEW:
{review}

KEY TAKEAWAYS:
"""
        
        logger.info("Prepared instruction to extract key takeaways from review")
        return instruction  

    @kernel_function(
        description="Rate a product in specific categories based on a review",
        name="rate_product"
    )
    async def rate_product(
        self, 
        review: t.Annotated[str, "The full text of the comprehensive review to base ratings on"]
    ) -> str:
        """
        Create a ratings summary instruction for a product based on the review content.
        
        Args:
            review: The comprehensive review text.
                    
        Returns:
            A JSON string containing ratings instructions for the LLM.
        """
        # Format instruction for rating generation
        instruction = f"""
Based on the following review, rate the product in each category on a scale of 1-10:
- Technical Innovation
- Market Fit
- Value Proposition
- Ease of Implementation
- Overall Rating

For each rating, provide a brief justification (1-2 sentences).

REVIEW:
{review}

Format your response as a JSON object with the following structure:
{{
  "ratings": {{
    "Technical Innovation": {{
      "score": <score>,
      "justification": "<brief justification>"
    }},
    "Market Fit": {{
      "score": <score>,
      "justification": "<brief justification>"
    }},
    "Value Proposition": {{
      "score": <score>,
      "justification": "<brief justification>"
    }},
    "Ease of Implementation": {{
      "score": <score>,
      "justification": "<brief justification>"
    }},
    "Overall Rating": {{
      "score": <score>,
      "justification": "<brief justification>"
    }}
  }}
}}

Ensure the response is valid JSON.
"""
        
        logger.info("Prepared instruction to generate product ratings")
        return instruction  

    @kernel_function(
        description="Generate pros and cons for a product based on a review",
        name="generate_pros_cons"
    )
    async def generate_pros_cons(
        self, 
        review: t.Annotated[str, "The full text of the comprehensive review to extract pros and cons from"]
    ) -> str:
        """
        Generate a structured list of pros and cons instruction based on the review.
        
        Args:
            review: The comprehensive review text.
                    
        Returns:
            A formatted instruction prompt for the LLM to generate pros and cons.
        """
        instruction = f"""
Based on the following review, generate a comprehensive list of pros and cons.
Identify at least 3 pros and 3 cons, with brief explanations for each.

REVIEW:
{review}

Format your response as follows:

## Pros
- [Pro 1]: [Brief explanation]
- [Pro 2]: [Brief explanation]
- [Pro 3]: [Brief explanation]
...

## Cons
- [Con 1]: [Brief explanation]
- [Con 2]: [Brief explanation]
- [Con 3]: [Brief explanation]
...
"""
        
        logger.info("Prepared instruction to generate pros and cons list")
        return instruction 