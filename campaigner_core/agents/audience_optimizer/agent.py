from campaigner_core.core.domain import Campaign
from campaigner_core.core.schemas import AgentInput, AgentResult, GovernanceBlock, AgentMetadata
from campaigner_core.agents.generic_mock import GenericMockAgent
from campaigner_core.infra.persistence import repo
import datetime

class AudienceOptimizerAgent(GenericMockAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config, agent_name="audience_optimizer")

    def process(self, input_data: AgentInput) -> AgentResult:
        campaign = repo.get(input_data.campaign_id)
        
        # 1. Timing Logic: Check 1 day before launch
        # Note: In a real scenario, we might return False if too early/late, but for MVP we just warn
        today = datetime.date.today()
        days_diff = (campaign.launch_date - today).days
        
        timing_note = "Timing Óptimo."
        if days_diff != 1:
            timing_note = f"Advertencia: Ejecutando {days_diff} días antes de la salida (Ideal: 1 día)."

        # 2. Segmentation Logic: Mock categories based on Campaign Category
        category_segments = {
            "Electro": ["Entusiastas Tecno", "Home Office", "Gamers"],
            "Belleza": ["Cuidado de Piel", "Compradores de Lujo", "Bienestar"],
            "Deco": ["Decoración Hogar", "Mudanzas Recientes", "DIY"],
            "Moda": ["Fashionistas", "Compradores de Temporada", "Marcadores de Tendencia"],
            "Deportes": ["Fitness", "Aventureros", "Deportes de Equipo"],
            "Calzado": ["Coleccionistas", "Buscadores de Confort", "Formal"],
            "Colchones": ["Buscadores de Calidad de Sueño", "Mejoras del Hogar"],
            "Otros": ["Interés General", "Cazadores de Ofertas"]
        }
        
        selected_segments = category_segments.get(campaign.category.value, ["Audiencia General"])
        
        # Mock Optimization
        original_count = campaign.total_sends or 50000
        optimized_count = int(original_count * 0.92) # 8% reduction via cleaner segmentation
        
        optimal_time = f"{campaign.launch_date}T10:00:00"
        
        return AgentResult(
            request_id=input_data.request_id,
            success=True,
            data={
                "optimization": {
                    "original_audience": original_count,
                    "optimized_audience": optimized_count,
                    "removed_segments": ["Emails Compartidos", "Inactivos > 180 días"],
                    "optimal_send_time": optimal_time,
                    "selected_segments": selected_segments,
                    "lift_prediction": "+15% Tasa de Apertura"
                }
            },
            governance=GovernanceBlock(
                confidence_score=0.95,
                explanation=f"Segmentación adaptada para {campaign.category.value}. {timing_note}",
                policy_checks=["Verificación de Timing", "Alineación de Categoría"],
                fallback_triggered=False
            ),
            metadata=AgentMetadata(
                agent_name="audience_optimizer",
                agent_version="2.0.0",
                execution_time_ms=250.0
            )
        )
