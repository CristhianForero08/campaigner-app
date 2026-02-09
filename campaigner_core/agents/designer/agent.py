from campaigner_core.core.domain import Campaign, CategoryType, ChannelType
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.config.settings import AgentConfig
from campaigner_core.agents.generic_mock import GenericMockAgent
from campaigner_core.infra.persistence import repo
import random

class DesignerAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="designer")

    def process(self, input_data: AgentInput) -> AgentResult:
        campaign = repo.get(input_data.campaign_id)
        if not campaign:
            return AgentResult(success=False, error="Campaign not found", request_id=input_data.request_id)

        # 1. Determine Color Palette based on Category
        palette = self._get_palette(campaign.category)
        
        # 2. Select Layout based on Channel
        layout = self._get_layout(campaign.channel)
        
        # 3. Generate Mock Assets
        assets = {
            "hero_banner": f"https://mock-assets.com/{campaign.brand}/{campaign.category}.jpg",
            "font_primary": "Inter, sans-serif",
            "font_secondary": "Merriweather, serif"
        }

        return AgentResult(
            request_id=input_data.request_id,
            success=True,
            data={
                "design_specs": {
                    "palette": palette,
                    "layout": layout,
                    "assets": assets,
                    "layout_type": layout # Added for frontend compatibility
                }
            },
            governance=GovernanceBlock(
                confidence_score=0.95,
                explanation=f"Diseño generado para {campaign.category.value} / {campaign.channel.value}",
                policy_checks=[],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name="designer",
                agent_version="1.0.0",
                execution_time_ms=50.0
            )
        )

    def _get_palette(self, category: CategoryType):
        if category == CategoryType.BELLEZA:
            return ["#FFC0CB", "#FFFFFF", "#333333"] # Rosa/Blanco
        elif category == CategoryType.ELECTRO:
            return ["#0000FF", "#000000", "#F0F0F0"] # Azul/Negro
        elif category == CategoryType.DEPORTES:
            return ["#FF0000", "#FFFFFF", "#000000"] # Rojo/Negro
        else:
            return ["#666666", "#CCCCCC", "#FFFFFF"] # Escala de Grises

    def _get_layout(self, channel: ChannelType):
        if channel == ChannelType.EMAIL:
            return "Columna Simple Optimizada"
        elif channel == ChannelType.WHATSAPP:
            return "Mensaje Compacto + Multimedia"
        else:
            return "Estándar"
