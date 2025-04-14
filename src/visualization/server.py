"""
Simple FastAPI server for agent discussion visualization.
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
import json
import logging
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import threading

# Import the simplified review board agent
from agents.orchestration import DocumentReviewOrchestrator


# Set up logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Define the path to template and static files
base_dir = Path(__file__).parent
templates_dir = base_dir / "templates"
static_dir = base_dir / "static"

# Create the directory if it doesn't exist
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# Active WebSocket connections
active_connections = []

# Review process state
review_state = {"is_running": False, "document_path": None, "title": None}


@app.get("/", response_class=HTMLResponse)
async def get():
    """Serve the main visualization page."""
    with open(templates_dir / "index.html") as f:
        return f.read()
   


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.post("/start-review")
async def start_review(request: Request):
    """Start the review process."""
    # Get JSON data from request
    request_data = await request.json()

    # Prevent multiple reviews from running simultaneously
    if review_state["is_running"]:
        await broadcast({"message": "A review is already in progress."})
        return {"status": "error", "message": "Review already in progress"}

    document_path = request_data.get("path")
    if not document_path:
        await broadcast({"message": "No document path provided."})
        return {"status": "error", "message": "No document path provided"}

    # Set review state
    review_state["is_running"] = True
    review_state["document_path"] = document_path
    review_state["title"] = request_data.get("title") or Path(document_path).stem

    # Start the review process in a background task
    asyncio.create_task(
        run_review(
            document_path=document_path,
            title=request_data.get("title"),
            discussion_rounds=request_data.get("discussion_rounds", 2),
            verbose=request_data.get("verbose", False),
        )
    )

    return {"status": "success", "message": "Review started"}


async def broadcast(message):
    """Broadcast a message to all connected WebSocket clients."""
    if not active_connections:
        logger.warning("No active WebSocket connections - message won't be delivered")
        return

    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
            disconnected.append(connection)

    # Remove any disconnected clients from the active connections list
    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)
            logger.info(
                f"Removed disconnected client. Remaining connections: {len(active_connections)}"
            )


async def broadcast_message(message):
    """
    Public function that can be imported by other modules to broadcast messages.
    This allows the agents to send messages to all connected clients.

    Args:
        message: The message to broadcast (must be JSON serializable)
    """
    logger.info(f"Server received broadcast request: {message.get('type', 'unknown')}")

    # Broadcast the message to all clients
    await broadcast(message)

    # Return success for confirmation
    return {"status": "broadcast_complete", "connections": len(active_connections)}


async def run_review(document_path, title=None, discussion_rounds=2, verbose=False):
    """Run the review process and broadcast messages."""
    try:
        await broadcast({"message": f"Starting review of {document_path}..."})

        # Read the document
        try:
            with open(document_path, "r", encoding="utf-8") as f:
                document_text = f.read()
        except FileNotFoundError:
            await broadcast(
                {"message": f"Error: Document not found at {document_path}"}
            )
            review_state["is_running"] = False
            return

        # Use filename as title if not provided
        if not title:
            title = Path(document_path).stem

        # Create the review board agent
        review_board = DocumentReviewOrchestrator()

        # Send updates about the process
        await broadcast({"message": f"Created review board for: {title}"})
        await broadcast(
            {
                "message": f"Starting document review with {discussion_rounds} discussion rounds..."
            }
        )

        # Run the review
        results = await review_board.evaluate_document(
            document=document_text,
            title=title,
            discussion_rounds=discussion_rounds,
            enable_visualization=True,
        )

        # Store the results
        output_dir = Path("/workspaces/pbod/review_results")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{title}_evaluation.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Also save the markdown file
        from utils.create_output import save_review_markdown

        md_path = save_review_markdown(results)

        # Send final message
        await broadcast(
            {
                "message": f"Review complete! Results saved to {output_path} and {md_path}",
            }
        )

        # Update review state
        review_state["is_running"] = False

    except Exception as e:
        logger.error(f"Error in review process: {e}")
        logger.exception("Full exception details:")
        await broadcast({"message": f"Error in review process: {str(e)}"})
        review_state["is_running"] = False


# Mount static files directory if it exists
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def start_server():
    """Start the visualization server."""
    host = "0.0.0.0"  # This allows access from the host when running in a container
    port = 8000

    def run_server():
        uvicorn.run(app, host=host, port=port)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    logger.info(f"Visualization server running at http://{host}:{port}")

    return f"http://{host}:{port}"


def main():
    """Main entry point function that can be imported by main.py"""
    server_url = start_server()
    
    print(f"\n{'='*70}")
    print("Technology Review Board running at:")
    print(f"{server_url}")
    print("Open this URL in a browser to analyze documents")
    print(f"{'='*70}\n")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nApplication stopped. Goodbye!")
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        logger.exception("Full exception details:")


if __name__ == "__main__":
    main()
