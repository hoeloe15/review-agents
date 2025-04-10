# Technology Review Board Visualization

A simple web interface for running document reviews with agent-based analysis.

## Overview

This system provides a web interface to the Technology Review Board agent-based document analysis system. Instead of using the command line, you can now:

1. Start the visualization server
2. Open the web interface
3. Enter a document path and options
4. Click "Start Review" to begin the process
5. Watch as different agents provide their analysis and discuss the document in real-time

## How It Works

The system uses a simple architecture:

1. **Web Server**: A FastAPI server provides the web interface and WebSocket connections for real-time updates
2. **Agent Process**: The same review board agents from the original system are used, but their output is captured and sent to the web interface
3. **Real-time Updates**: The web interface displays agent messages as they are generated

## Agent Process Explained

The review process has three main phases:

1. **Individual Analyses**: Specialized agents analyze the document from different perspectives
   - Innovative Visionary (like Steve Jobs): Focuses on innovative potential and vision
   - Critical Reviewer: Identifies flaws, challenges, and implementation issues
   - Business Advisor: Evaluates business viability and market potential

2. **Agent Discussion**: The agents discuss their findings and insights
   - Lead Technology Advisor moderates the discussion
   - Each agent contributes from their unique perspective
   - Multiple rounds of discussion can occur (configurable)

3. **Final Synthesis**: The Lead Technology Advisor synthesizes all feedback into a final recommendation

## Using the Interface

1. **Basic Usage**: Enter a document path and click "Start Review"
2. **Advanced Options**: Click "Show Advanced Options" to access additional settings:
   - Custom Title: Provide a custom title for the review
   - Discussion Focus: Set a specific focus for the agent discussion
   - Discussion Rounds: Set the number of discussion rounds (1-3)
   - Enable/Disable Discussion: Turn the discussion phase on/off
   - Verbose Output: Enable more detailed output

## Running the Server

To start the visualization server:

```bash
cd /workspaces/pbod
python src/visualization_server.py
```

Then open a browser to the URL shown in the terminal (typically http://0.0.0.0:8000).

## Output

The system saves the review results in two formats:
1. JSON file: Contains the raw data from all agents
2. Markdown file: A formatted report of the review

Both files are saved in the `/workspaces/pbod/review_results/` directory.

## Differences from Command Line Version

This web interface provides the same functionality as the command line version (`main.py`), but with a more user-friendly interface and real-time visualization. The underlying agent system is the same. 