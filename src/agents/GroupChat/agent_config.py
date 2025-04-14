"""
Configuration module for document review templates.

This module contains configuration settings for the document review templates
used to format prompts and recommendations.
"""


def get_initial_prompt_template() -> str:
    """Get the template for the initial document review prompt."""
    return """
# Technology Review: {title}

You are a Technology Review Board evaluating the following document. Each board member has a specific perspective and expertise. 
Your goal is to thoroughly analyze the document and provide constructive feedback.

## THE DOCUMENT:
{document}

## BOARD MEMBERS:
- LeadTechnologyAdvisor: Balances perspectives and guides the discussion
- InnovativeVisionary: Identifies future potential and transformative possibilities
- CriticalReviewer: Focuses on technical challenges and implementation concerns
- BusinessAdvisor: Evaluates market viability and business opportunity

## DISCUSSION GUIDELINES:
- Be concise - limit comments to 3-4 sentences
- Stay focused on your area of expertise
- Address other members by name when responding to their points
- Aim for a balanced assessment considering all viewpoints
- Ensure all board members contribute to the discussion
- Engage with points raised by other members

{lead_advisor}, please begin by introducing the review session and asking for initial assessments from each board member.
"""


def get_recommendation_prompt_template() -> str:
    """Get the template for the recommendation prompt."""
    return """
Based on our discussion of the document "{title}", please provide a comprehensive final recommendation.

Key points from our discussion:
{discussion_summary}

Your recommendation should include:
1. Executive Summary (2-3 sentences)
2. Key Strengths (3-5 bullet points)
3. Areas for Improvement (3-5 bullet points)
4. Recommended Next Steps (3-5 actionable items)
5. Overall Assessment (including a score from 1-10)

Format your response as a well-structured recommendation document with clear sections and bullet points.
"""


def get_fallback_recommendation_template() -> str:
    """Get the template for a fallback recommendation when an error occurs."""
    return (
        """An error occurred while generating the recommendation. Please try again."""
    )
