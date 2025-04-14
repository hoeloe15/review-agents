# Review Writer Agent System

This system uses Semantic Kernel agents to generate comprehensive, multi-perspective reviews based on input prompts. The system consists of specialized agents that collaborate to analyze different aspects of a product or technology, coordinated by a main reviewer agent.

## System Architecture

The Review Writer system uses the following agents:

1. **Review Coordinator (Main Agent)**: Leads the review process, asks questions, synthesizes information, and produces the final review.

2. **Technology Reviewer**: Analyzes technical features, capabilities, market positioning, and value proposition.

3. **Relevance Analyst**: Assesses use cases, relevance, and compares with alternative solutions.

4. **Implementation Analyst**: Evaluates implementation complexity, integration capabilities, scalability, and maintenance requirements.

## How It Works

1. The system takes an input prompt describing what needs to be reviewed.
2. The Review Coordinator asks specialized agents for their analysis.
3. Each specialized agent provides their perspective on the topic.
4. The Review Coordinator synthesizes all input into a comprehensive review.
5. The final review includes technical assessment, relevance analysis, implementation considerations, and more.

## Usage

### Basic Usage

```python
import asyncio
from src.agents.review_writer import ReviewWriterSystem

async def generate_review():
    # Initialize the review writer system
    review_system = ReviewWriterSystem()
    
    # Define the review prompt
    prompt = "Review the new XYZ Quantum Computing platform, focusing on its technical capabilities, market relevance, and implementation requirements."
    
    # Generate the review
    async for message in review_system.generate_review(prompt):
        print(f"## {message.name}:\n{message.content}\n")

if __name__ == "__main__":
    asyncio.run(generate_review())
```

### Advanced Usage with Plugins

The system includes plugins for specialized review functionality:

```python
import asyncio
from src.agents.review_writer import ReviewWriterSystem, setup_kernel_with_plugins
from semantic_kernel.kernel_pydantic import KernelBaseModel

async def generate_review_with_plugins():
    # Setup kernel with review plugins
    kernel = setup_kernel_with_plugins()
    
    # Initialize with custom kernel and handle responses
    # ... custom implementation ...

if __name__ == "__main__":
    asyncio.run(generate_review_with_plugins())
```

## Future Enhancements

1. **Web Connection**: Enable the Relevance Analyst to perform real-time research.
2. **Internal Document Connection**: Allow the Implementation Analyst to access internal documentation.
3. **Technical Documentation Integration**: Connect to product documentation for more accurate technical analysis.
4. **Custom Prompts**: Allow customization of prompts and evaluation criteria.

## Requirements

- Semantic Kernel
- Azure OpenAI service configured with appropriate deployments

## System Prompt Customization

Each agent uses a specialized system prompt that can be customized. The default prompts focus on:

- **Technology Reviewer**: Technical assessment and market positioning
- **Relevance Analyst**: Use cases, alternatives, and comparative analysis
- **Implementation Analyst**: Implementation considerations and requirements
- **Review Coordinator**: Synthesis and organization of the final review

## Examples

### Example Input Prompt

```
Review the OpenAI GPT-4 language model focusing on its capabilities for enterprise applications, comparing it with alternatives, and discussing implementation requirements.
```

### Example Output Structure

The generated review will follow this structure:

```
# Comprehensive Review: [Product Name]

## Executive Summary
[A brief summary of the review findings]

## Technical Assessment
[Analysis of technical features and capabilities]

## Relevance and Alternatives Analysis
[Analysis of relevance, use cases, and alternatives]

## Implementation Considerations
[Analysis of implementation requirements and considerations]

## Conclusion
[Overall assessment and recommendations]
``` 