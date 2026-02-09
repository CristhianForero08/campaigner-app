from typing import List, Dict, Any
from campaigner_core.core.schemas import AgentInput, AgentResult, AgentMode
from campaigner_core.orchestrator.registry import registry
from campaigner_core.core.logging import get_logger

logger = get_logger("ORCHESTRATOR.FLOW")

class FlowExecutor:
    """
    Executes a predefined sequence of agents.
    """
    
    async def execute_flow(
        self, 
        flow_steps: List[str], 
        initial_payload: Dict[str, Any],
        campaign_id: str,
        mode: AgentMode = AgentMode.STANDARD
    ) -> Dict[str, AgentResult]:
        
        results: Dict[str, AgentResult] = {}
        context: Dict[str, Any] = initial_payload.copy() # Shared context across flow
        
        logger.info(f"Starting flow execution: {flow_steps} for Campaign {campaign_id}")

        for agent_name in flow_steps:
            try:
                agent = registry.get_agent(agent_name)
                
                # Build Input
                agent_input = AgentInput(
                    campaign_id=campaign_id,
                    payload=context, # Pass accumulated context/payload
                    mode=mode,
                    context=context
                )
                
                # Execute
                logger.info(f"Executing step: {agent_name}")
                result = agent.process(agent_input)
                results[agent_name] = result

                # Stop on failure
                if not result.success:
                    logger.error(f"Flow stopped at {agent_name} with error: {result.error}")
                    break
                
                # Update context with output to feed next agent
                if result.data:
                    context.update(result.data)

            except Exception as e:
                logger.error(f"Critical error executing {agent_name}: {e}")
                break
        
        logger.info("Flow execution finished.")
        return results

flow_executor = FlowExecutor()
