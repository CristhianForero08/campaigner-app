import time
from campaigner_core.core.interfaces import AgentInterface
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.config.settings import AgentConfig
from campaigner_core.core.logging import get_logger

class GenericMockAgent(AgentInterface):
    """
    Reusable mock agent for rapid scaffolding of the platform ecosystem.
    Returns approval/pass decisions.
    """
    def __init__(self, config: AgentConfig, agent_name: str):
        self.config = config
        self.name = agent_name
        self.logger = get_logger(f"AGENT.{agent_name.upper()}")

    def get_name(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.config.version

    def health_check(self) -> bool:
        return True

    def process(self, input_data: AgentInput) -> AgentResult:
        start_time = time.time()
        self.logger.info(f"Mock Processing: {input_data.request_id}")
        
        # Simulate work
        time.sleep(0.05)
        
        return AgentResult(
            request_id=input_data.request_id,
            success=True,
            data={
                "status": "APPROVED",
                "notes": f"Checked by {self.name}",
                "metrics": {"quality": 1.0}
            },
            governance=GovernanceBlock(
                confidence_score=0.99,
                explanation=f"{self.name} simulation passed all checks.",
                policy_checks=["Mock Policy A"],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name=self.name,
                agent_version=self.get_version(),
                model_used="mock-v1",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        )
