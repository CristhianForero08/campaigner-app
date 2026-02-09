from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from campaigner_core.core.schemas import AgentInput, AgentResult

class AuditLogger(ABC):
    @abstractmethod
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log a structured audit event."""
        pass

class AgentInterface(ABC):
    """Base contact for all Agents in the platform."""
    
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_version(self) -> str:
        pass

    @abstractmethod
    def process(self, input_data: AgentInput) -> AgentResult:
        """Main execution entry point."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        pass
