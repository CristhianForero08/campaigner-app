from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel

from campaigner_core.orchestrator.registry import registry
from campaigner_core.orchestrator.execution import flow_executor
from campaigner_core.core.schemas import AgentInput, AgentResult, AgentMode
from campaigner_core.core.domain import Campaign
from campaigner_core.infra.persistence import repo

router = APIRouter()

class ExecutionRequest(BaseModel):
    # payload: Dict[str, Any] # No longer needed if fetching from DB, but kept for overrides if needed
    campaign_id: str
    mode: AgentMode = AgentMode.STANDARD

@router.get("/campaigns", response_model=List[Campaign])
async def list_campaigns():
    return repo.list_all()

@router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign: Campaign):
    repo.save(campaign)
    return campaign

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    campaign = repo.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, campaign: Campaign):
    existing = repo.get(campaign_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Ensure ID consistency
    if campaign.id != campaign_id:
        raise HTTPException(status_code=400, detail="Campaign ID in body must match URL")

    repo.save(campaign)
    return campaign

@router.get("/agents")
async def list_agents():
    return registry.list_agents()

@router.post("/agents/{agent_name}/execute", response_model=AgentResult)
async def execute_agent(agent_name: str, request: ExecutionRequest):
    try:
        agent = registry.get_agent(agent_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 1. Prepare Input
    input_data = AgentInput(
        campaign_id=request.campaign_id,
        payload={}, # Agent will fetch generic payload from Campaign ID
        mode=request.mode
    )
    
    # 2. Execute
    result = agent.process(input_data)
    
    # 3. Persist Result if successful
    if result.success:
        campaign = repo.get(request.campaign_id)
        if campaign:
            campaign.agent_outputs[agent_name] = result.model_dump(mode='json')
            repo.save(campaign)
            
    return result
