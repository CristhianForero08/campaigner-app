from campaigner_core.core.domain import Campaign
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.config.settings import AgentConfig
from campaigner_core.agents.generic_mock import GenericMockAgent
from campaigner_core.infra.persistence import repo

class CRMEngineerAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="crm_engineer")

    def process(self, input_data: AgentInput) -> AgentResult:
        campaign = repo.get(input_data.campaign_id)
        
        # 1. Dependency Check: Verify previous agents
        required_agents = ["copywriter", "brand_guardian", "legal_compliance", "designer", "campaign_qa"]
        previous_results = campaign.agent_outputs or {}
        
        missing_agents = [agent for agent in required_agents if agent not in previous_results or not previous_results[agent].get("success")]
        
        if missing_agents:
            return AgentResult(
                request_id=input_data.request_id,
                success=False,
                error=f"Cannot proceed. Missing successful execution from: {', '.join(missing_agents)}",
                metadata=AgentMetadata(
                    agent_name=self.name,
                    agent_version=self.get_version(),
                    execution_time_ms=50.0
                )
            )

        # 2. Scoring Logic
        # Calculate average confidence from previous agents
        scores = []
        for agent in required_agents:
            if agent in previous_results:
                # Safely access confidence_score, assuming structure matches Schema
                gov = previous_results[agent].get("governance", {})
                score = gov.get("confidence_score", 0.0)
                scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Threshold
        SCORE_THRESHOLD = 0.7
        is_passing = avg_score >= SCORE_THRESHOLD
        
        # Mock Logic: Check audience size (Technical validation)
        audience_size = campaign.total_sends or 0
        technical_valid = audience_size > 1000 and audience_size < 1000000
        
        final_success = is_passing and technical_valid
        
        explanation = f"Análisis de Scoring: Confianza Promedio {avg_score:.2f} (Umbral {SCORE_THRESHOLD}). Validaciones técnicas aprobadas."
        if not is_passing:
            explanation = f"Fallo de Scoring: Confianza Promedio {avg_score:.2f} está por debajo del umbral {SCORE_THRESHOLD}. Revisar pasos anteriores."
        elif not technical_valid:
            explanation = f"Fallo Técnico: Tamaño de audiencia {audience_size} fuera de rango (1k-1M)."
        
        return AgentResult(
            request_id=input_data.request_id,
            success=final_success,
            data={
                "validation": {
                    "audience_size": audience_size,
                    "data_quality_score": 0.98,
                    "workflow_score": avg_score,
                    "technical_flags": [] if technical_valid else ["Error en Tamaño de Audiencia"]
                }
            },
            governance=GovernanceBlock(
                confidence_score=avg_score, # Function of previous agents
                explanation=explanation,
                policy_checks=["Scoring de Flujo", "Límites Técnicos"],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name="crm_engineer",
                agent_version="2.0.0",
                execution_time_ms=120.0
            )
        )
