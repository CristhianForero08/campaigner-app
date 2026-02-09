import sqlite3
import os
import json
from typing import List, Optional
from datetime import date
from campaigner_core.core.domain import Campaign
from campaigner_core.core.logging import get_logger

logger = get_logger("INFRA.PERSISTENCE")

class CampaignRepository:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Check if running in Vercel environment
            if os.environ.get("VERCEL"):
                self.db_path = "/tmp/campaigner.db"
                logger.info(f"Running in Vercel, using ephemeral DB at {self.db_path}")
            else:
                self.db_path = "campaigner.db"
        else:
            self.db_path = db_path
            
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite scheme."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                request_date TEXT,
                channel TEXT,
                subchannel TEXT,
                brand TEXT,
                category TEXT,
                total_sends INTEGER,
                launch_date TEXT,
                ok_to_send INTEGER,
                link_commercial TEXT,
                link_image TEXT,
                segment TEXT,
                legal_date TEXT,
                type TEXT,
                comment TEXT,
                status TEXT,
                agent_outputs TEXT
            )
        ''')
        
        # Migration: Check if 'segment' column exists, if not add it
        try:
            c.execute("SELECT segment FROM campaigns LIMIT 1")
        except sqlite3.OperationalError:
            logger.info("Migrating DB: Adding 'segment' column")
            c.execute("ALTER TABLE campaigns ADD COLUMN segment TEXT")

        # Migration: Check if 'legal_date' column exists, if not add it
        try:
            c.execute("SELECT legal_date FROM campaigns LIMIT 1")
        except sqlite3.OperationalError:
            logger.info("Migrating DB: Adding 'legal_date' column")
            c.execute("ALTER TABLE campaigns ADD COLUMN legal_date TEXT")

        # Migration: Check if 'type' column exists
        try:
            c.execute("SELECT type FROM campaigns LIMIT 1")
        except sqlite3.OperationalError:
            logger.info("Migrating DB: Adding 'type' column")
            c.execute("ALTER TABLE campaigns ADD COLUMN type TEXT")
            
        # Migration: Check if 'comment' column exists
        try:
            c.execute("SELECT comment FROM campaigns LIMIT 1")
        except sqlite3.OperationalError:
            logger.info("Migrating DB: Adding 'comment' column")
            c.execute("ALTER TABLE campaigns ADD COLUMN comment TEXT")
            
        conn.commit()
        conn.close()

    def save(self, campaign: Campaign):
        """Save or Update a Campaign."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Serialize complex fields
        agent_outputs_json = json.dumps(campaign.agent_outputs)
        
        c.execute('''
            INSERT OR REPLACE INTO campaigns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign.id,
            campaign.request_date.isoformat(),
            campaign.channel.value,
            campaign.subchannel,
            campaign.brand,
            campaign.category.value,
            campaign.total_sends,
            campaign.launch_date.isoformat(),
            1 if campaign.ok_to_send else 0,
            str(campaign.link_commercial),
            str(campaign.link_image) if campaign.link_image else None,
            campaign.segment,
            campaign.legal_date.isoformat() if campaign.legal_date else None,
            campaign.type.value,
            campaign.comment,
            campaign.status,
            agent_outputs_json
        ))
        conn.commit()
        conn.close()
        logger.info(f"Saved Campaign {campaign.id}")

    def get(self, campaign_id: str) -> Optional[Campaign]:
        """Retrieve a specific campaign by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            return None
        
        return self._row_to_campaign(row)

    def list_all(self) -> List[Campaign]:
        """List all campaigns."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM campaigns ORDER BY request_date DESC")
        rows = c.fetchall()
        conn.close()
        
        return [self._row_to_campaign(row) for row in rows]

    def _row_to_campaign(self, row) -> Campaign:
        """Helper to convert SQL row to Campaign Object."""
        data = dict(row)
        
        # Map DB columns back to Domain Aliases (so Pydantic parses them correctly)
        # Note: We are reconstructing using the ALIASES because that's what Campaign(**dict) expects
        # if using populate_by_name=True, we can also use internal names.
        # But we stored flat. Let's reconstruct internal dictionary.
        
        campaign_dict = {
            "id": data["id"],
            "Fecha_Solicitud": data["request_date"],
            "Canal": data["channel"],
            "Subcanal": data["subchannel"],
            "Marca": data["brand"],
            "Categoria": data["category"],
            "Total_Envios": data["total_sends"],
            "Fecha_Salida": data["launch_date"],
            "OK_Para_Envio": bool(data["ok_to_send"]),
            "Link_COM": data["link_commercial"],
            "Link_Imagen": data["link_image"],
            "Segmento": data["segment"] if "segment" in data.keys() else "General",
            "Fecha_Legal": data["legal_date"] if "legal_date" in data.keys() else None,
            "Tipo": data["type"] if "type" in data.keys() else "Monetizado", # Default to monetizado for old records
            "Comentario": data["comment"] if "comment" in data.keys() else None,
            "status": data["status"],
            "agent_outputs": json.loads(data["agent_outputs"]) if data["agent_outputs"] else {}
        }
        
        return Campaign(**campaign_dict)

# Singleton for easy access
repo = CampaignRepository()
