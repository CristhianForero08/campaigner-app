import importlib
from typing import Dict, Type
from campaigner_core.config.settings import settings
from campaigner_core.core.interfaces import AgentInterface
from campaigner_core.core.logging import get_logger

logger = get_logger("ORCHESTRATOR.REGISTRY")

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentInterface] = {}

    def register_agent(self, agent_instance: AgentInterface):
        """Manually register an instantiated agent."""
        name = agent_instance.get_name()
        self._agents[name] = agent_instance
        logger.info(f"Registered agent: {name} (v{agent_instance.get_version()})")

    def get_agent(self, name: str) -> AgentInterface:
        """Retrieve an agent by name."""
        agent = self._agents.get(name)
        if not agent:
            raise KeyError(f"Agent '{name}' not found in registry.")
        return agent

    def list_agents(self) -> Dict[str, str]:
        """Return dict of agent_name -> status."""
        return {
            name: "READY" if agent.health_check() else "UNHEALTHY"
            for name, agent in self._agents.items()
        }

    def load_agents_from_config(self):
        """
        Dynamically load enabled agents based on config.
        Assumption: Agents are located at platform.agents.<name>.agent.AgemtClass
        """
        if not settings:
            logger.warning("No settings loaded, skipping dynamic load.")
            return

        for name, config in settings.agents.items():
            if not config.enabled:
                logger.info(f"Skipping disabled agent: {name}")
                continue
            
            try:
                # Dynamic import magic
                # Expecting: platform.agents.copywriter.agent
                module_path = f"campaigner_core.agents.{name}.agent"
                module = importlib.import_module(module_path)
                
                # Expecting class named 'CopywriterAgent' or similar, 
                # but better to look for AgentInterface subclass
                agent_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, AgentInterface) and 
                        attr is not AgentInterface and
                        attr.__module__ == module.__name__): # Ensure it's defined in this module
                        agent_class = attr
                        break
                
                if agent_class:
                    instance = agent_class(config) # Inject config
                    self.register_agent(instance)
                else:
                    logger.error(f"No AgentInterface subclass found in {module_path}")

            except ImportError as e:
                logger.error(f"Failed to import agent module '{name}': {e}")
            except Exception as e:
                logger.error(f"Failed to initialize agent '{name}': {e}")

# Global instance
registry = AgentRegistry()
