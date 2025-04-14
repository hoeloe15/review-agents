"""
Review Plugins for Review Writer System

This module provides plugin functions for the Review Writer Agent system,
allowing agents to perform specialized tasks related to review generation.
"""

import logging
import json
from typing import List, Dict, Any

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_function_context import KernelFunctionContext

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
    async def synthesize_review(self, context: KernelFunctionContext) -> str:
        """
        Format and synthesize a comprehensive review from multiple inputs.
        
        Args:
            context: Contains 'tech_review', 'relevance_review', 'implementation_review',
                    'product_name', and 'summary' as input variables.
                    
        Returns:
            A formatted comprehensive review that synthesizes all inputs.
        """
        tech_review = context["tech_review"]
        relevance_review = context["relevance_review"]
        implementation_review = context["implementation_review"]
        product_name = context["product_name"]
        summary = context["summary"]
        
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
    async def extract_key_takeaways(self, context: KernelFunctionContext) -> str:
        """
        Extract and format key takeaways from a comprehensive review.
        
        Args:
            context: Contains 'review' as input variable.
                    
        Returns:
            A formatted list of key takeaways from the review.
        """
        review = context["review"]
        
        # Format for extraction instruction
        instruction = f"""
Extract 3-5 key takeaways from the following review. 
Format them as a bullet-point list.

REVIEW:
{review}

KEY TAKEAWAYS:
"""
        
        logger.info("Extracted key takeaways from review")
        return instruction  # This will be processed by the LLM

    @kernel_function(
        description="Rate a product in specific categories",
        name="rate_product"
    )
    async def rate_product(self, context: KernelFunctionContext) -> str:
        """
        Create a ratings summary for a product based on the review content.
        
        Args:
            context: Contains 'review' as input variable.
                    
        Returns:
            A JSON string containing ratings in different categories.
        """
        review = context["review"]
        
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
        
        logger.info("Generated product ratings")
        return instruction  # This will be processed by the LLM

    @kernel_function(
        description="Generate pros and cons for a product",
        name="generate_pros_cons"
    )
    async def generate_pros_cons(self, context: KernelFunctionContext) -> str:
        """
        Generate a structured list of pros and cons based on the review.
        
        Args:
            context: Contains 'review' as input variable.
                    
        Returns:
            A formatted list of pros and cons.
        """
        review = context["review"]
        
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
        
        logger.info("Generated pros and cons list")
        return instruction  # This will be processed by the LLM 