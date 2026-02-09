from datetime import date
from campaigner_core.core.domain import Campaign
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.config.settings import AgentConfig
from campaigner_core.agents.generic_mock import GenericMockAgent
from campaigner_core.infra.persistence import repo

class LegalComplianceAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="legal_compliance")

    def process(self, input_data: AgentInput) -> AgentResult:
        campaign = repo.get(input_data.campaign_id)
        if not campaign:
            return AgentResult(success=False, error="Campaign not found", request_id=input_data.request_id)

        score = 1.0
        issues = []
        
        # Rule 1: Monetized campaigns must have a Legal Date or Comment explanation
        if campaign.type.value == "Monetizado":
            if not campaign.legal_date and not campaign.comment:
                score -= 0.2
                issues.append("Campaña monetizada sin Fecha Legal o explicación")
                
        # Rule 2: Launch Date Validation
        if campaign.launch_date < campaign.request_date:
            score -= 0.5
            issues.append("La Fecha de Salida no puede ser anterior a la Fecha de Solicitud")

        # Rule 3: Valid Links
        if not str(campaign.link_commercial).startswith("https"):
            score -= 0.1
            issues.append("El Link Comercial debe ser HTTPS")

        success = score > 0.8
        explanation = "Cumple con Legales" if success else f"Problemas de cumplimiento: {', '.join(issues)}"

        return AgentResult(
            request_id=input_data.request_id,
            success=success,
            data={
                "checks": {
                    "valid_dates": len([i for i in issues if "Fecha" in i]) == 0,
                    "https_links": "HTTPS" in str(campaign.link_commercial)
                },
                "issues": issues,
                "compliance": { # Added for frontend compatibility
                    "required_disclaimers": ["Términos y Condiciones", "Política de Privacidad"] if campaign.type.value == "Monetizado" else []
                }
            },
            governance=GovernanceBlock(
                confidence_score=round(score, 2),
                explanation=explanation,
                policy_checks=[],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name="legal_compliance",
                agent_version="1.0.0",
                execution_time_ms=35.0
            )
        )
