# Multi-Agent Review System Demo

This project demonstrates a collaborative AI system where multiple specialized agents work together to generate comprehensive reviews. The system uses Microsoft Semantic Kernel to orchestrate communication between agents, each having specific expertise.

## Overview

The demo shows a real-time, visual representation of how multiple AI agents collaborate to create a comprehensive review:

1. **ReviewCoordinator**: Orchestrates the review process, asks targeted questions, and synthesizes the final review
2. **TechnologyReviewer**: Evaluates technical features, capabilities, and marketplace positioning
3. **RelevanceAnalyst**: Assesses use cases, alternatives, and comparative advantages/disadvantages
4. **ImplementationAnalyst**: Analyzes implementation requirements, scalability, and maintenance considerations

## Features

- **Live Agent Interaction**: Watch as agents communicate in real-time
- **Process Transparency**: See which agent is active and view their "thinking" process
- **Visual Differentiation**: Each agent has a distinct visual style in the conversation
- **Interactive Experience**: Input any topic you want to have reviewed

## Prerequisites

- Python 3.9+
- Azure OpenAI API access (or regular OpenAI API)

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure your environment variables in a `.env` file:
   ```
   # For Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2023-05-15
   
   # OR for OpenAI
   OPENAI_API_KEY=your-api-key
   OPENAI_MODEL=gpt-4o
   ```

## Running the Demo

1. Start the application:
   ```
   python src/main.py
   ```
2. Open your browser and navigate to `http://localhost:8000`
3. Enter a topic for review in the input field and click "Start Review"
4. Watch the agents collaborate in real-time

## Architecture

- **FastAPI Backend**: Handles API endpoints and SSE (Server-Sent Events) streaming
- **Semantic Kernel**: Manages agent orchestration and AI interactions
- **Frontend**: Simple HTML/CSS/JS interface for visualizing the agent interaction

## Project Structure

```
├── src/
│   ├── main.py               # Application entry point
│   ├── server.py             # FastAPI server implementation
│   ├── review_system.py      # Agent orchestration logic
│   ├── kernel_provider.py    # Semantic Kernel configuration
│   ├── prompts.py            # Agent system prompts
│   ├── plugins/              # Semantic Kernel plugins
│   └── utils.py              # Utility functions
├── static/                   # Static assets for the web interface
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript
├── templates/                # HTML templates
├── .env                      # Environment variables (create this)
└── requirements.txt          # Project dependencies
```

## Extending the Demo

- Add more specialized agents to the system
- Implement additional plugins to give agents more tools
- Enhance the UI with more detailed agent states

## License

MIT