from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class AgentMode(str, Enum):
    STANDARD = "STANDARD"
    DEGRADED = "DEGRADED"  # Fallback logic only
    AUDIT_ONLY = "AUDIT_ONLY"

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    DISABLED = "DISABLED"

class AgentInput(BaseModel):
    """Standardized input wrapper for all agents."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: Optional[str] = None
    trace_id: Optional[str] = None
    payload: Dict[str, Any] = Field(..., description="Agent-specific input data")
    mode: AgentMode = Field(default=AgentMode.STANDARD)
    context: Dict[str, Any] = Field(default_factory=dict, description="Shared flow context")

class GovernanceBlock(BaseModel):
    """Explainability and safety metadata."""
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str = Field(..., description="Human-readable reason for the output")
    policy_checks: List[str] = Field(default_factory=list, description="List of passed policy checks")
    fallback_triggered: bool = False

class AgentMetadata(BaseModel):
    agent_name: str
    agent_version: str
    model_used: Optional[str] = None
    execution_time_ms: float
    token_usage: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentResult(BaseModel):
    """Standardized output wrapper for all agents."""
    request_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    governance: Optional[GovernanceBlock] = None
    metadata: AgentMetadata
