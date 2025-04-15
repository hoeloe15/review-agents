# Project Status and Next Steps: Multi-Agent Review System Demo

## 1. Overall Goal

The primary objective is to create a **dynamic, visual demonstration** of a multi-agent system built using Python and Semantic Kernel. This demo should:

1.  **Show Live Interaction:** Display the conversation between agents turn-by-turn in real-time, rather than just presenting a final static output.
2.  **Visualize Agent Activity:** Clearly indicate which agent (`ReviewCoordinator`, `TechnologyReviewer`, etc.) is currently active.
3.  **Provide Process Transparency:** Make the agents' "thinking" process visible by showing:
    *   The agent's stated **intent** or plan for its turn.
    *   Any **tool/plugin function calls** it requests, including the function name and arguments.
    *   Ideally, the *reasoning* behind using a specific tool.
4.  **Use a Web Frontend:** Present this live visualization in a web browser interface.
5.  **Enable Interactivity:** Allow a user (e.g., for a demo) to input a new review prompt and observe the system generating the review live.

## 2. Current System Status

*   **Technology Stack:** Python, Semantic Kernel, Azure OpenAI (configured via `dotenv`), standard Python logging.
*   **Core Components:**
    *   `src/kernel_provider.py`: Manages Kernel setup and adds the `Reviewer` plugin.
    *   `src/plugins/review_plugin.py`: Contains functions for review processing (`synthesize_review`, `extract_key_takeaways`, `rate_product`, `generate_pros_cons`).
    *   `src/prompts.py`: Defines system instructions for the four agents (`ReviewCoordinator`, `TechnologyReviewer`, `RelevanceAnalyst`, `ImplementationAnalyst`).
    *   `src/review_system.py`: Contains the `ReviewSystem` class which initializes agents.
    *   `src/main.py`: Main execution script, sets up logging, initializes `ReviewSystem`, runs the review generation, and generates reports.
    *   `src/utils.py`: Contains helper functions like `format_agent_message`.
*   **Orchestration:**
    *   Successfully refactored **away from `AgentGroupChat`**.
    *   `ReviewSystem.generate_review` now uses a **manual `async` loop** to iterate through the defined agent sequence (`self.agent_sequence`) for a fixed number of turns (currently 9).
    *   Manages `ChatHistory` internally within the loop.
    *   Invokes agents using `await current_agent.invoke(history)` (using positional `history`) and processes the resulting async generator to get the final message for the turn.
    *   Adds the agent's response message to the `ChatHistory`.
    *   Returns the complete `ChatHistory` object upon completion.
*   **Logging & Reporting:**
    *   Configured Python logging sends `INFO`+ messages to console and `DEBUG`+ messages to `app.log` (overwritten each run).
    *   `main.py` generates a static Markdown file (`review_report.md`) after execution, containing the full conversation history.
    *   The `COORDINATOR_PROMPT` includes a rule instructing the agent to state its plan and explain *why* it intends to use a tool *before* making the call.
    *   The report generation code in `main.py` includes logic to *detect* and display tool call requests (checking `message.items` for `function_call` or `tool_calls` attributes).
*   **Known Issues / Current State:**
    *   **Agent Flow:** Specialist agents (`TechnologyReviewer`, etc.) still tend to generate full analyses/reviews in response to the Coordinator's initial questions, rather than just answering the question directly. The Coordinator sometimes synthesizes prematurely.
    *   **Tool Call Reporting:** The `review_report.md` file currently **does not show the `**Tool Calls:**` section**. This indicates the detection logic in `main.py` (checking `message.items`, `function_call`, `tool_calls`) isn't correctly identifying the structure of the tool call requests within the `ChatMessageContent` objects as returned by the current Semantic Kernel version/setup.
    *   **No Live View:** The system currently runs entirely in the backend and produces only static output files (`app.log`, `review_report.md`). There is no web server, streaming, or frontend UI.

## 3. Next Steps to Reach Goal

These steps should be followed in order:

1.  **Debug Tool Call Reporting in `review_report.md`:**
    *   **Goal:** Reliably extract and display requested tool calls (function name, arguments) in the static Markdown report.
    *   **Action:**
        1.  Temporarily modify the report generation loop in `src/main.py` (around line 130-150) to add detailed debug logging of the `message` object received from the history. Specifically, log `message.items` and potentially `dir(message)` and `vars(message)` to understand its structure.
            *Example Debug Line:* `logger.debug(f"Inspecting message items for tool calls: {message.items}")`
        2.  Run `src/main.py` once.
        3.  Carefully examine `app.log` to find these debug messages and determine the *actual* structure used by Semantic Kernel to represent tool call requests within the `ChatMessageContent` (it might be nested differently, use different attribute names like `tool_calls`, etc.).
        4.  Adjust the `if hasattr(...)` conditions and attribute access logic in the report generation loop in `src/main.py` to match the observed structure.
        5.  Re-run and verify that the `**Tool Calls:**` section now appears correctly in `review_report.md` when the Coordinator uses tools.

2.  **Refine Agent Prompts for Better Flow Control:**
    *   **Goal:** Ensure specialists answer direct questions first, and the Coordinator manages the conversation flow more explicitly (distinguishing Q&A rounds from synthesis rounds).
    *   **Action:**
        1.  Edit `src/prompts.py`. Modify the `RULES` section of `TECH_REVIEWER_PROMPT`, `RELEVANCE_ANALYST_PROMPT`, and `IMPLEMENTATION_ANALYST_PROMPT`.
            *Add Rule:* `When responding to a direct question from the ReviewCoordinator, focus *only* on answering that specific question based on your area of expertise and the overall topic. Do not generate a full review structure (like Pros/Cons, Ratings) unless specifically asked to do so in *that turn*.`
        2.  Edit `src/prompts.py`. Modify the `RULES` section of `COORDINATOR_PROMPT`.
            *Refine Rule/Add:* Make it more explicit about controlling rounds. E.g., `In the first round, your plan should be *only* to ask specific questions to each specialist. Clearly state this and tell them to *only* answer the question. In later rounds, after receiving answers, your plan might be to synthesize the information using the appropriate tool.`

3.  **Implement Streaming Backend (e.g., FastAPI + Server-Sent Events):**
    *   **Goal:** Create a web server that can run the agent orchestration and stream events (agent turn start, message content, tool calls) to connected clients in real-time.
    *   **Action:**
        1.  Add `fastapi` and `uvicorn` to project dependencies (e.g., `requirements.txt`) and install.
        2.  Create `src/server.py`. Set up a basic FastAPI application.
        3.  Implement an SSE endpoint (e.g., `/stream`) using `StreamingResponse` and an `asyncio.Queue` or similar mechanism for sending events.
        4.  Refactor `src/review_system.py`: Modify `generate_review`. Instead of returning `ChatHistory`, it should accept the SSE `Queue` (or a callback function) as an argument. Inside the loop, after processing each `final_message` (and extracting tool calls), put structured event dictionaries (e.g., `{\"event\": \"agent_message\", \"agent\": agent_name, \"content\": message_content, \"tool_calls\": [...]}`) onto the queue.
        5.  Refactor `src/main.py`: Remove the direct call to `generate_review`. Instead, `main` should primarily start the Uvicorn server to run the FastAPI app defined in `src/server.py`.
        6.  In `src/server.py`, create another endpoint (e.g., POST `/generate`) that accepts the review `prompt`. This endpoint will initialize the `ReviewSystem`, create the SSE queue, run `review_system.generate_review(prompt, queue)` in the background (e.g., using `asyncio.create_task`), and return a confirmation to the caller.

4.  **Develop Live Frontend UI:**
    *   **Goal:** Create a simple web page that connects to the stream and displays the agent interactions live.
    *   **Action:**
        1.  Create an HTML file (e.g., `static/index.html`). Add basic structure (e.g., a `div` to hold the conversation).
        2.  Add JavaScript: Use the `EventSource` API to connect to the `/stream` endpoint.
        3.  Implement an `onmessage` event handler in JavaScript. Parse the incoming event data (JSON).
        4.  Based on the event type (`agent_message`, `tool_call`, etc.), dynamically create and append HTML elements to the conversation `div` to display the agent's name, message, and tool usage information as it arrives.
        5.  Add basic styling (CSS).
        6.  Configure FastAPI to serve the static HTML/CSS/JS files.

5.  **Refine Visualization and Interactivity:**
    *   **Goal:** Enhance the UI/UX for clarity and allow user input.
    *   **Action:**
        *   Improve frontend styling to clearly distinguish agents, messages, and tool calls.
        *   Add an input field and button to the HTML page.
        *   Add JavaScript to capture the input prompt and send it to the `/generate` endpoint on the backend when the button is clicked.
        *   Ensure the Coordinator's stated reasoning for tool calls is clearly displayed.
        *   (Optional) Explore capturing and displaying the *results* of tool calls if feasible.
