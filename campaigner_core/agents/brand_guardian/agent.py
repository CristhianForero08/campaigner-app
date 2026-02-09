from typing import Dict, Any
from campaigner_core.core.domain import Campaign
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.config.settings import AgentConfig
from campaigner_core.agents.generic_mock import GenericMockAgent
from campaigner_core.infra.persistence import repo

class BrandGuardianAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="brand_guardian")
        self.forbidden_words = ["spam", "junk", "estafa", "100% free", "garantizado"]

    def process(self, input_data: AgentInput) -> AgentResult:
        # Load Campaign
        campaign = repo.get(input_data.campaign_id)
        if not campaign:
            return AgentResult(success=False, error="Campaign not found", request_id=input_data.request_id)

        # Logic
        score = 1.0
        issues = []
        
        # Check brand consistency
        if not campaign.brand:
            score -= 0.3
            issues.append("Falta el Nombre de la Marca")

        # Check for forbidden words in Comment
        if campaign.comment:
            for bad_word in self.forbidden_words:
                if bad_word in campaign.comment.lower():
                    score -= 0.2
                    issues.append(f"Palabra prohibida en comentarios: '{bad_word}'")
        
        # Check Copywriter output if available
        copy_out = campaign.agent_outputs.get("copywriter")
        if copy_out and copy_out["success"]:
            content = copy_out["data"].get("content", {})
            body = content.get("body", "") + content.get("subject", "")
            for bad_word in self.forbidden_words:
                if bad_word in body.lower():
                    score -= 0.4
                    issues.append(f"Palabra prohibida en el Copy: '{bad_word}'")
        
        success = score > 0.7
        explanation = "Cumple con las Guías de Marca" if success else f"Se encontraron problemas: {', '.join(issues)}"
        
        return AgentResult(
            request_id=input_data.request_id,
            success=success,
            data={
                "checks": {
                    "forbidden_words": len(issues) == 0,
                    "tone_consistency": True
                },
                "issues": issues,
                "validation": { # Added for frontend compatibility
                     "tone_match": True,
                     "forbidden_words_found": issues
                }
            },
            governance=GovernanceBlock(
                confidence_score=round(score, 2),
                explanation=explanation,
                policy_checks=[],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name="brand_guardian",
                agent_version="1.0.0",
                execution_time_ms=42.0
            )
        )
