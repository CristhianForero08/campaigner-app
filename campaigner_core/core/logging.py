import logging
import json
from datetime import datetime
from typing import Dict, Any
from campaigner_core.core.interfaces import AuditLogger

# Configure basic logging for the platform
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ConsoleAuditLogger(AuditLogger):
    """
    Simple audit logger that prints structured JSON to stdout.
    In production, this would write to a DB or Splunk.
    """
    def __init__(self, source: str):
        self.logger = logging.getLogger(f"AUDIT.{source}")
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        # writing as JSON string for easy parsing by external tools
        self.logger.info(json.dumps(event))

def get_logger(name: str):
    return logging.getLogger(name)
