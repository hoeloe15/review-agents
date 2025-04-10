# Technology Review Board

A simple agent-based system for evaluating technology documents through group discussion.

## Overview

This system implements a group chat of agents with different perspectives to review technology documents:

- **Lead Technology Advisor**: Guides the discussion and provides balanced insights
- **Innovative Visionary**: Focuses on potential and transformative aspects
- **Critical Reviewer**: Identifies flaws, challenges, and limitations
- **Business Advisor**: Evaluates business viability and market potential

The agents engage in a debate-style discussion analyzing the document from their unique perspectives.

## Key Features

- **Multi-Agent Group Chat**: True debate-style discussion between agents with different personas
- **Semantic Kernel Integration**: Uses SK's AgentGroupChat for sophisticated agent interactions
- **Real-Time Visualization**: Web interface to watch the agent discussion unfold
- **Markdown Output**: Generates a cleanly formatted review report

## Setup

### API Key Configuration

Before running the system, you need to set up your OpenAI API key:

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o  # or another suitable model
   ```

3. If using Azure OpenAI, uncomment and configure the Azure settings in the `.env` file.

### Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python src/main.py [document_path] [options]
```

Options:
- `--title TEXT`: Custom title for the review
- `--output PATH`: Custom output path for results
- `--rounds INTEGER`: Number of discussion rounds (default: 2)
- `--verbose`: Show detailed logging
- `--visualize`: Open web visualization

Example:
```bash
python src/main.py samples/sample.txt --rounds 3 --visualize
```

### Web Interface

To use the web interface:

1. Start the visualization server:
   ```bash
   python src/visualization_server.py
   ```

2. Open a browser to http://0.0.0.0:8000
3. Enter the document path and options
4. Click "Start Review" to begin

## Architecture

This system uses Semantic Kernel's AgentGroupChat to enable sophisticated agent interactions:

1. **ChatCompletionAgent**: Individual agents with specific personas and instructions
2. **AgentGroupChat**: Manages the conversation flow between agents
3. **DocumentReviewChat**: Coordinates the review process and visualization
4. **Visualization Server**: Provides real-time web visualization of discussions

## Output

Results are saved in two formats:
1. JSON file with the full results data
2. Markdown file with a formatted report

Files are saved to `/workspaces/pbod/review_results/` by default.

## How It Works

The system simulates a debate between different expert personas:

1. The document is presented to the group with specific review instructions
2. Each agent analyzes the document from their unique perspective
3. Agents engage in a multi-round discussion, responding to each other's points
4. The Lead Advisor guides the conversation and synthesizes insights
5. A final recommendation is generated based on the full discussion

## Troubleshooting

### Error with Agent Names
If you see validation errors about agent names not matching patterns, check that spaces in agent names have been replaced with underscores in the code.

### API Key Issues
Make sure your `.env` file has the correct API key and model settings. The system requires at least OpenAI API access.

### No Response or Slow Responses
Semantic Kernel requires a bit of time for the agents to process the document and respond. Be patient during the first few exchanges.

## Future Enhancements

1. **Custom Agent Creation**: Allow users to define their own agent personas
2. **Enhanced Visualization**: More interactive web interface with agent relationships
3. **Domain-Specific Agents**: Specialized agents for different types of documents
4. **Memory and Knowledge**: Incorporate external knowledge for more informed discussions