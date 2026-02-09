import yaml
from typing import Dict, Any, List
from pydantic import BaseModel
from pathlib import Path

class AgentConfig(BaseModel):
    enabled: bool
    version: str
    provider: str
    model: str = "default"
    temperature: float = 0.7
    max_tokens: int = 500
    fallback_enabled: bool = True
    extra: Dict[str, Any] = {}

class SecurityConfig(BaseModel):
    allowed_roles: List[str]
    audit_level: str

class PlatformSettings(BaseModel):
    agents: Dict[str, AgentConfig]
    security: SecurityConfig

    @classmethod
    def load_from_yaml(cls, path: str = "campaigner_core/config/agents.yaml") -> "PlatformSettings":
        try:
            with open(path, "r") as f:
                raw_config = yaml.safe_load(f)
            
            # Parse agents with flexible extra fields
            agents_dict = {}
            for name, cfg in raw_config.get("agents", {}).items():
                # Extract known fields, put rest in extra
                # Simple approach: let Pydantic ignore extras or handle them. 
                # For now, just direct mapping.
                agents_dict[name] = AgentConfig(**cfg)
            
            return cls(
                agents=agents_dict,
                security=SecurityConfig(**raw_config.get("security", {}))
            )
        except Exception as e:
            print(f"Error loading config: {e}")
            # Return safe default or raise
            raise e

# Singleton instance
try:
    settings = PlatformSettings.load_from_yaml()
except FileNotFoundError:
    # For initial testing if file not found locally relative to execution
    settings = None
