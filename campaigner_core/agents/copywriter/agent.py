import time
from campaigner_core.core.interfaces import AgentInterface
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata, AgentMode
from campaigner_core.config.settings import AgentConfig
from campaigner_core.core.logging import get_logger

# Domain & Persistence
from campaigner_core.infra.persistence import repo
from campaigner_core.agents.copywriter.validator import InputValidator
from campaigner_core.agents.copywriter.generator import ContentGenerator

logger = get_logger("AGENT.COPYWRITER")

class CopywriterAgent(AgentInterface):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = "copywriter"
        self.validator = InputValidator()
        self.generator = ContentGenerator()
        
    def get_name(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.config.version

    def health_check(self) -> bool:
        return True

    def process(self, input_data: AgentInput) -> AgentResult:
        start_time = time.time()
        logger.info(f"Processing Request {input_data.request_id} for Campaign {input_data.campaign_id}")
        
        # 1. Fetch Context (Campaign)
        campaign = repo.get(input_data.campaign_id)
        if not campaign:
            return self._error_result(input_data, "Campaign not found", start_time)

        try:
            # 2. Validation
            warnings = self.validator.validate(campaign)
            
            # 3. Logic / AI Generation
            if input_data.mode == AgentMode.DEGRADED or not self.config.enabled:
                # Fallback
                generated_content = {
                    "text": "Fallback content due to degraded mode.", 
                    "template": "fallback_v1"
                }
                explanation = "Generated using rules only (Degraded Mode)."
                confidence = 1.0
                fallback = True
            else:
                # "AI" Generation
                result_raw = self.generator.generate(campaign)
                generated_content = result_raw["final_content"]
                explanation = f"Generated {result_raw['tone_applied']} content using {result_raw['template_used']}."
                confidence = 0.88 # Mock score
                fallback = False

            # 4. Construct Result
            response_data = {
                "channel": campaign.channel.value,
                "content": generated_content,
                "status": "READY_FOR_APPROVAL"
            }

            return AgentResult(
                request_id=input_data.request_id,
                success=True,
                data=response_data,
                governance=GovernanceBlock(
                    confidence_score=confidence,
                    explanation=explanation,
                    policy_checks=["Date Coherence", "Asset Check"],
                    fallback_triggered=fallback
                ),
                metadata=AgentMetadata(
                    agent_name=self.name,
                    agent_version=self.get_version(),
                    model_used=self.config.model,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    token_usage=200
                )
            )

        except Exception as e:
            logger.error(f"Error in copywriter process: {e}")
            return self._error_result(input_data, str(e), start_time)

    def _error_result(self, input_data, error_msg, start_time):
        return AgentResult(
            request_id=input_data.request_id,
            success=False,
            error=error_msg,
            metadata=AgentMetadata(
                agent_name=self.name,
                agent_version=self.get_version(),
                execution_time_ms=(time.time() - start_time) * 1000
            )
        )
