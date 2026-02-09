from campaigner_core.core.domain import Campaign
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.config.settings import AgentConfig
from campaigner_core.agents.generic_mock import GenericMockAgent
from campaigner_core.infra.persistence import repo

class CampaignQAAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="campaign_qa")

    def process(self, input_data: AgentInput) -> AgentResult:
        campaign = repo.get(input_data.campaign_id)
        if not campaign:
            return AgentResult(success=False, error="Campaign not found", request_id=input_data.request_id)
        
        checklist = {}
        score = 1.0
        
        # 1. Check Copywriter
        if "copywriter" in campaign.agent_outputs and campaign.agent_outputs["copywriter"]["success"]:
            checklist["Copy Listo"] = True
        else:
            checklist["Copy Listo"] = False
            score -= 0.3

        # 2. Check Legal
        if "legal_compliance" in campaign.agent_outputs and campaign.agent_outputs["legal_compliance"]["success"]:
            checklist["Legal Aprobado"] = True
        else:
            checklist["Legal Aprobado"] = False
            score -= 0.2 # Warning
            
        # 3. Check Design (Optional but good)
        if "designer" in campaign.agent_outputs:
            checklist["Diseño Listo"] = True
        else:
            checklist["Diseño Listo"] = False
            
        # 4. Check Manual Approval
        if campaign.ok_to_send:
            checklist["Aprobación Manual"] = True
        else:
            checklist["Aprobación Manual"] = False
            score -= 0.5 # Critical

        ready_to_launch = score > 0.8
        
        return AgentResult(
            request_id=input_data.request_id,
            success=ready_to_launch,
            data={
                "checklist": checklist,
                "final_score": round(score, 2)
            },
            governance=GovernanceBlock(
                confidence_score=round(score, 2),
                explanation="Listo para Lanzamiento" if ready_to_launch else "QA Fallido: Revisar items faltantes",
                policy_checks=[],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name="campaign_qa",
                agent_version="1.0.0",
                execution_time_ms=25.0
            )
        )
