"""
FastAPI server for the multi-agent review system demo.

This module provides a web server with endpoints for:
1. Serving static files (HTML, CSS, JS)
2. Streaming the conversation between agents
"""

import logging
import asyncio
import json
import signal
import sys
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from review_system import ReviewSystem

# Set up logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Multi-Agent Review System Demo")

# Create the ReviewSystem instance
review_system = ReviewSystem()

# Templates directory for serving the HTML
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Model for review requests
class ReviewRequest(BaseModel):
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/review")
async def start_review(review_request: ReviewRequest):
    """Start a new review and return a session ID."""
    # For simplicity, we're not using session IDs in this demo
    # But in a production app, you'd want to track different review sessions
    return {"status": "started", "prompt": review_request.prompt}

@app.get("/api/stream")
async def stream_review(prompt: str):
    """Stream the review generation process."""
    
    async def event_generator():
        try:
            async for message in review_system.generate_review_stream(prompt):
                # Convert the message to a JSON string
                json_data = json.dumps(message)
                yield f"data: {json_data}\n\n"
                # Small delay to make the stream more visible in the UI
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}", exc_info=True)
            error_msg = {"agent_name": "System", "content": f"Error: {str(e)}", "status": "error"}
            json_data = json.dumps(error_msg)
            yield f"data: {json_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# Handle graceful shutdown
def handle_sigterm(signal, frame):
    """Handle SIGTERM signal for graceful shutdown."""
    logger.info("Received shutdown signal, exiting...")
    sys.exit(0)

# Main function to run the server with uvicorn
def start_server():
    """Start the FastAPI server."""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    import uvicorn
    
    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server() 