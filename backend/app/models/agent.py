"""Agent-related data models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Agent roles in the multi-agent system."""

    GENERATOR = "generator"
    VALIDATOR = "validator"
    RANKER = "ranker"


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "IDLE"
    WORKING = "WORKING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ToolUseEvent(BaseModel):
    """Event emitted when an agent uses a tool."""

    agent_role: AgentRole = Field(..., description="Agent that used the tool")
    tool_name: str = Field(..., description="Name of the tool used")
    tool_input: Dict[str, Any] = Field(..., description="Tool input parameters")
    tool_output: Optional[Dict[str, Any]] = Field(None, description="Tool output (if completed)")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[float] = Field(None, description="Tool execution duration in ms")
    
    # For Agent Teams hooks
    hook_type: Optional[str] = Field(
        None, description="Hook type (PreToolUse, PostToolUse, etc.)"
    )
    session_id: Optional[str] = Field(None, description="Agent session ID")
    tool_use_id: Optional[str] = Field(None, description="Tool use ID from Claude")


class AgentMessage(BaseModel):
    """Message between agents during debate."""

    from_agent: AgentRole = Field(..., description="Sending agent")
    to_agent: AgentRole = Field(..., description="Receiving agent")
    message: str = Field(..., description="Message content")
    message_type: str = Field(
        default="feedback", description="Message type (feedback, rebuttal, agreement, etc.)"
    )
    
    hypothesis_id: Optional[str] = Field(None, description="Related hypothesis ID")
    round_number: int = Field(..., ge=1, description="Debate round number")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DebateRound(BaseModel):
    """One round of debate between agents."""

    round_number: int = Field(..., ge=1, description="Round number")
    messages: List[AgentMessage] = Field(default_factory=list, description="Messages in this round")
    
    # Generator's proposal
    generator_hypotheses: List[str] = Field(
        default_factory=list, description="Hypothesis IDs proposed by generator"
    )
    
    # Validator's feedback
    validator_feedback: List[str] = Field(
        default_factory=list, description="Feedback from validator"
    )
    validator_scores: Dict[str, float] = Field(
        default_factory=dict, description="Scores from validator"
    )
    
    # Generator's response
    generator_revisions: List[str] = Field(
        default_factory=list, description="Revised hypothesis IDs"
    )
    
    # Consensus
    consensus_reached: bool = Field(default=False, description="Whether consensus was reached")
    consensus_hypotheses: List[str] = Field(
        default_factory=list, description="Hypotheses that reached consensus"
    )
    
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)


class AgentState(BaseModel):
    """Current state of an agent."""

    role: AgentRole = Field(..., description="Agent role")
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="Current status")
    
    # Current task
    current_task: Optional[str] = Field(None, description="Description of current task")
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Task progress")
    
    # Stats
    total_tool_uses: int = Field(default=0, description="Total number of tool uses")
    total_tokens_used: int = Field(default=0, description="Total tokens used")
    total_cost_usd: float = Field(default=0.0, description="Total cost in USD")
    
    # Timestamps
    started_at: Optional[datetime] = Field(None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)


class DebateSession(BaseModel):
    """Complete debate session between agents."""

    session_id: str = Field(..., description="Unique session ID")
    
    # Agents involved
    generator_state: AgentState
    validator_state: AgentState
    ranker_state: AgentState
    
    # Debate rounds
    rounds: List[DebateRound] = Field(default_factory=list, description="Debate rounds")
    max_rounds: int = Field(default=3, description="Maximum rounds allowed")
    
    # Final results
    final_hypotheses: List[str] = Field(
        default_factory=list, description="Final hypothesis IDs"
    )
    consensus_reached: bool = Field(default=False, description="Overall consensus")
    
    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    total_duration_seconds: Optional[float] = Field(None)
    
    # WebSocket streaming
    stream_url: Optional[str] = Field(None, description="WebSocket URL for real-time updates")


class StreamEvent(BaseModel):
    """Event sent via WebSocket for real-time updates."""

    event_type: str = Field(..., description="Event type (progress, tool_use, message, etc.)")
    session_id: str = Field(..., description="Debate session ID")
    
    # Event data (flexible)
    data: Dict[str, Any] = Field(..., description="Event-specific data")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "event_type": "progress",
                "session_id": "sess_abc123",
                "data": {
                    "agent": "generator",
                    "progress_percent": 45.0,
                    "message": "Generating hypothesis 3 of 5...",
                },
                "timestamp": "2026-03-07T01:00:00Z",
            }
        }
