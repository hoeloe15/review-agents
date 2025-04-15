# Semantic Kernel AgentGroupChat Termination Issue Investigation

## Problem Statement

An `AgentGroupChat` configured with `KernelFunctionTerminationStrategy` appears to terminate prematurely, even when the underlying termination function returns a message indicating the chat should continue (e.g., "incomplete") and the `result_parser` is configured to correctly interpret this message as `False`.

The logs show:
1. The termination function (e.g., `termination`) is invoked.
2. The function's result is correctly returned (e.g., `ChatMessageContent` with `content='incomplete'`).
3. The `KernelFunctionTerminationStrategy` logs indicate the function was invoked and show the result.
4. **Despite the result indicating non-completion, the strategy logs `should terminate: True` immediately after.**
5. The `AgentGroupChat` stops invoking further agents.

This occurs after the very first turn by the initial agent (`ReviewCoordinator` in this case).

## Code Context

- **Branch:** `debug/termination-strategy`
- **Relevant Files:**
    - `src/main.py`: Entry point, invokes the chat.
    - `src/review_system.py`: Defines agents and `AgentGroupChat` with strategies.
    - `src/kernel_provider.py`: Sets up the kernel and loads plugins.
    - `src/prompts.py`: Contains agent instructions and strategy prompts.
    - `src/plugins/review_plugin.py`: Contains functions potentially callable by agents.
- **Key Configuration (`src/review_system.py` -> `_create_group_chat`):**
    ```python
    # ... inside AgentGroupChat definition ...
    termination_strategy=KernelFunctionTerminationStrategy(
        agents=[self.review_coordinator], # Only coordinator triggers check
        function=termination_function,    # Uses TERMINATION_PROMPT
        kernel=self.kernel,
        result_parser=lambda result: "complete" in result.value[0].content.lower() if result.value and result.value[0].content else False, # Parses content
        history_variable_name="lastmessage",
        all_history_variable_name="history",
        maximum_iterations=25,
        history_reducer=termination_history_reducer,
    )
    ```
- **Termination Prompt (`src/prompts.py`):** Designed to return "incomplete" until specific conditions are met.

## How to Reproduce

1. Ensure you are on the `debug/termination-strategy` branch.
2. Make sure `.env` file is configured with valid Azure OpenAI or OpenAI credentials.
3. Run the command: `uv run src/main.py`
4. Observe the logs and console output. Note that the chat stops after the first `ReviewCoordinator` message, and the logs show `should terminate: True` despite the termination function returning "incomplete".

## Debugging Steps & Further Investigation

1.  **Examine `KernelFunctionTerminationStrategy` Source:**
    - Dive into the Semantic Kernel library source code for `KernelFunctionTerminationStrategy.should_terminate`.
    - Trace the logic: How does it use the `result_parser`? Are there other conditions (besides the parser result and `maximum_iterations`) that could cause it to return `True`? Is there a default behavior if the parser throws an error (even though logs don't show one)?
    - Pay attention to how it interacts with the list of `agents` provided to it (in this case, just `[self.review_coordinator]`).

2.  **Simplify the `result_parser`:**
    - Temporarily replace the lambda with a full `def` function that includes detailed logging:
      ```python
      # Add this definition within the ReviewSystem class or globally
      def parse_termination(result) -> bool:
          # Make sure logger is accessible or pass it in/use print
          print(f"DEBUG: Termination parser received result: {result}") # Use print for simplicity here
          if not result or not result.value or not result.value[0].content:
              print("DEBUG: Termination parser: No result or content found, returning False.")
              return False
          content = result.value[0].content.lower()
          print(f"DEBUG: Termination parser: Checking content '{content}' for 'complete'.")
          is_complete = "complete" in content
          print(f"DEBUG: Termination parser: Returning {is_complete}")
          return is_complete

      # ... in termination_strategy in _create_group_chat ...
      result_parser=parse_termination, # Reference the function
      # ...
      ```
    - Rerun and check the detailed parser logs against the strategy's final decision. *Remember to adjust logging level or use print if logger isn't easily accessible inside the lambda replacement.*

3.  **Check Strategy State:**
    - Are there any internal state variables within the `KernelFunctionTerminationStrategy` instance that might persist across calls incorrectly? (Less likely, but possible).

4.  **Test with `DefaultTerminationStrategy`:**
    - Temporarily switch *only* the termination strategy back to `DefaultTerminationStrategy(maximum_iterations=...)` while keeping the `KernelFunctionSelectionStrategy`. Does the chat proceed for the specified iterations? This helps isolate whether the issue is solely within `KernelFunctionTerminationStrategy` or a combination.

5.  **Vary `agents` Parameter:**
    - What happens if the `agents` parameter in `KernelFunctionTerminationStrategy` is set to `None` (check all agents) or includes other agents? Does the behavior change?

6.  **Minimum Reproducible Example:**
    - Try creating an even smaller, self-contained script outside this project structure that *only* sets up a minimal `AgentGroupChat` with two dummy agents and the `KernelFunctionTerminationStrategy` configured similarly. Can the premature termination be reproduced there? This helps eliminate interference from other parts of the application.

## Expected Outcome

The `AgentGroupChat` should continue invoking agents based on the `KernelFunctionSelectionStrategy` until the `KernelFunctionTerminationStrategy`'s `result_parser` correctly evaluates the termination function's output as `True` (i.e., the function returns "complete"), or the `maximum_iterations` limit is reached. It should not terminate when the parser returns `False`.