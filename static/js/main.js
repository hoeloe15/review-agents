/**
 * Multi-Agent Review System Demo
 * 
 * This script handles:
 * 1. Form submission to start a review
 * 2. Connection to the server-sent events stream
 * 3. Rendering the conversation in real-time
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const reviewForm = document.getElementById('review-form');
    const promptInput = document.getElementById('prompt');
    const startButton = document.getElementById('start-button');
    const reviewSection = document.getElementById('review-section');
    const conversation = document.getElementById('conversation');
    const statusMessage = document.getElementById('status-message');
    const thinkingIndicator = document.getElementById('thinking-indicator');

    // Event source for SSE
    let eventSource = null;

    // Track current thinking agent
    let currentThinkingMessage = null;

    // Handle form submission
    reviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const prompt = promptInput.value.trim();
        if (!prompt) return;

        // Disable form while review is in progress
        promptInput.disabled = true;
        startButton.disabled = true;

        // Show review section
        reviewSection.classList.remove('hidden');

        // Clear previous conversation
        conversation.innerHTML = '';

        // Update status
        statusMessage.textContent = 'Starting review generation...';

        try {
            // Connect to the event stream
            connectToEventStream(prompt);
        } catch (error) {
            console.error('Error starting review:', error);
            statusMessage.textContent = `Error: ${error.message}`;

            // Re-enable form
            promptInput.disabled = false;
            startButton.disabled = false;
        }
    });

    /**
     * Connect to the server-sent events stream
     */
    function connectToEventStream(prompt) {
        // Close any existing connection
        if (eventSource) {
            eventSource.close();
        }

        // Create a new connection
        const encodedPrompt = encodeURIComponent(prompt);
        eventSource = new EventSource(`/api/stream?prompt=${encodedPrompt}`);

        // Handle connection open
        eventSource.onopen = () => {
            console.log('SSE connection established');
            statusMessage.textContent = 'Connected to stream. Generating review...';
        };

        // Handle incoming messages
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Received data:', data);

                // Handle different message types
                handleStreamMessage(data);
            } catch (error) {
                console.error('Error parsing message:', error, event.data);
            }
        };

        // Handle errors
        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            statusMessage.textContent = 'Connection error. Please try again.';

            // Close the connection
            eventSource.close();
            eventSource = null;

            // Re-enable form
            promptInput.disabled = false;
            startButton.disabled = false;
        };
    }

    /**
     * Handle a message from the stream
     */
    function handleStreamMessage(data) {
        const { agent_name, content, turn, status } = data;

        // Update status message based on the agent
        if (status === 'thinking') {
            statusMessage.textContent = `${agent_name} is thinking...`;
            thinkingIndicator.classList.remove('hidden');

            // Create a thinking message placeholder
            const thinkingMsg = createMessageElement(agent_name, '...', turn);
            thinkingMsg.classList.add('thinking');
            conversation.appendChild(thinkingMsg);

            // Store reference to update later
            currentThinkingMessage = thinkingMsg;

            // Scroll to bottom
            scrollToBottom();
            return;
        }

        // Hide thinking indicator for completed messages
        if (status === 'complete' || status === 'error') {
            // If there was a thinking message, remove it
            if (currentThinkingMessage) {
                currentThinkingMessage.remove();
                currentThinkingMessage = null;
            }

            // Create the actual message
            const messageEl = createMessageElement(agent_name, content, turn);
            conversation.appendChild(messageEl);

            // Update status
            statusMessage.textContent = `Turn ${turn}: ${agent_name} responded`;
            thinkingIndicator.classList.add('hidden');

            // Scroll to bottom
            scrollToBottom();
        }

        // If this is the end notification
        if (status === 'end') {
            statusMessage.textContent = 'Review generation complete!';
            thinkingIndicator.classList.add('hidden');

            // Re-enable form
            promptInput.disabled = false;
            startButton.disabled = false;

            // Close the connection
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
        }
    }

    /**
     * Create a message element for the conversation
     */
    function createMessageElement(agentName, content, turn) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${agentName}`;

        const header = document.createElement('div');
        header.className = 'message-header';

        const nameSpan = document.createElement('span');
        nameSpan.className = `agent-name ${agentName}`;
        nameSpan.textContent = agentName;

        const turnSpan = document.createElement('span');
        turnSpan.className = 'turn-number';
        turnSpan.textContent = turn ? `Turn ${turn}` : '';

        header.appendChild(nameSpan);
        header.appendChild(turnSpan);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content || '';

        messageEl.appendChild(header);
        messageEl.appendChild(contentDiv);

        return messageEl;
    }

    /**
     * Scroll the conversation container to the bottom
     */
    function scrollToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }
}); 