from campaigner_core.config.settings import AgentConfig
from campaigner_core.agents.generic_mock import GenericMockAgent

class AnalyticsAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="analytics")
