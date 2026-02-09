from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import date
from pydantic import BaseModel, Field, HttpUrl
import uuid

class ChannelType(str, Enum):
    EMAIL = "Email"
    WHATSAPP = "Whatsapp"
    SMS = "SMS"
    PUSH = "Push"
    APP = "App"
    TRIGGER = "Trigger"

class CategoryType(str, Enum):
    ELECTRO = "Electro"
    BELLEZA = "Belleza"
    DECO = "Deco"
    COLCHONES = "Colchones"
    CALZADO = "Calzado"
    MODA = "Moda"
    DEPORTES = "Deportes"
    OTROS = "Otros"

class CampaignType(str, Enum):
    MONETIZADO = "Monetizado"
    CASA = "Casa"

class Campaign(BaseModel):
    """
    Core Domain Entity for a Campaign.
    Maps external Spanish inputs to internal English fields for better code quality,
    while supporting the required input JSON format.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Required Fields (Mapped from User Spec)
    request_date: date = Field(..., alias="Fecha_Solicitud")
    channel: ChannelType = Field(..., alias="Canal")
    subchannel: str = Field(..., alias="Subcanal")
    brand: str = Field(..., alias="Marca")
    category: CategoryType = Field(..., alias="Categoria")
    total_sends: int = Field(..., alias="Total_Envios")
    launch_date: date = Field(..., alias="Fecha_Salida")
    ok_to_send: bool = Field(..., alias="OK_Para_Envio")
    link_commercial: HttpUrl = Field(..., alias="Link_COM")
    link_image: Optional[HttpUrl] = Field(None, alias="Link_Imagen")
    segment: str = Field(..., alias="Segmento")
    legal_date: Optional[date] = Field(None, alias="Fecha_Legal")
    type: CampaignType = Field(..., alias="Tipo")
    comment: Optional[str] = Field(None, alias="Comentario")

    # Internal Status Fields
    status: str = "DRAFT"
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Fecha_Solicitud": "2023-10-25",
                "Canal": "Email",
                "Subcanal": "Newsletter",
                "Marca": "Samsung",
                "Categoria": "Electro",
                "Total_Envios": 5000,
                "Fecha_Salida": "2023-10-30",
                "OK_Para_Envio": True,
                "Link_COM": "https://www.samsung.com/ar/",
                "Link_Imagen": "https://images.samsung.com/is/image/samsung/p6pim/ar/feature/164555232/ar-feature-big-screen-big-entertainment-534346808"
            }
        }
