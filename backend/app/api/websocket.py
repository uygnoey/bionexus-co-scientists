"""WebSocket router for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

from app.core.logging import get_logger
from app.models.agent import StreamEvent

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        # session_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session ID
        """
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Remove WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session ID
        """
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info(f"WebSocket disconnected: {session_id}")

    async def send_event(self, session_id: str, event: StreamEvent) -> None:
        """Send event to all connections for a session.
        
        Args:
            session_id: Session ID
            event: Event to send
        """
        if session_id not in self.active_connections:
            return
        
        event_json = event.model_dump_json()
        
        # Send to all connections
        disconnected = set()
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(event_json)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            self.active_connections[session_id].discard(conn)

    async def broadcast(self, event: StreamEvent) -> None:
        """Broadcast event to all connections.
        
        Args:
            event: Event to broadcast
        """
        event_json = event.model_dump_json()
        
        for session_id, connections in self.active_connections.items():
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_text(event_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected.add(connection)
            
            for conn in disconnected:
                connections.discard(conn)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for real-time updates.
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID to subscribe to
    """
    await manager.connect(websocket, session_id)
    
    try:
        # Send initial connection event
        from datetime import datetime
        
        welcome_event = StreamEvent(
            event_type="connected",
            session_id=session_id,
            data={"message": "Connected to hypothesis generation stream"},
            timestamp=datetime.utcnow(),
        )
        await websocket.send_text(welcome_event.model_dump_json())
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            
            # Echo back (for ping/pong)
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    pong_event = StreamEvent(
                        event_type="pong",
                        session_id=session_id,
                        data={"timestamp": datetime.utcnow().isoformat()},
                        timestamp=datetime.utcnow(),
                    )
                    await websocket.send_text(pong_event.model_dump_json())
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)


async def send_progress_event(
    session_id: str,
    agent: str,
    progress: float,
    message: str,
) -> None:
    """Send progress update event.
    
    Args:
        session_id: Session ID
        agent: Agent name
        progress: Progress percentage (0-100)
        message: Progress message
    """
    from datetime import datetime
    
    event = StreamEvent(
        event_type="progress",
        session_id=session_id,
        data={
            "agent": agent,
            "progress_percent": progress,
            "message": message,
        },
        timestamp=datetime.utcnow(),
    )
    
    await manager.send_event(session_id, event)


async def send_hypothesis_event(
    session_id: str,
    hypothesis_id: str,
    hypothesis_text: str,
    score: float,
) -> None:
    """Send new hypothesis event.
    
    Args:
        session_id: Session ID
        hypothesis_id: Hypothesis ID
        hypothesis_text: Hypothesis text
        score: Hypothesis score
    """
    from datetime import datetime
    
    event = StreamEvent(
        event_type="hypothesis",
        session_id=session_id,
        data={
            "hypothesis_id": hypothesis_id,
            "text": hypothesis_text,
            "score": score,
        },
        timestamp=datetime.utcnow(),
    )
    
    await manager.send_event(session_id, event)


async def send_complete_event(
    session_id: str,
    num_hypotheses: int,
    generation_time: float,
) -> None:
    """Send completion event.
    
    Args:
        session_id: Session ID
        num_hypotheses: Number of generated hypotheses
        generation_time: Total generation time
    """
    from datetime import datetime
    
    event = StreamEvent(
        event_type="complete",
        session_id=session_id,
        data={
            "num_hypotheses": num_hypotheses,
            "generation_time_seconds": generation_time,
        },
        timestamp=datetime.utcnow(),
    )
    
    await manager.send_event(session_id, event)
