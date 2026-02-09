from typing import Dict, Any
from campaigner_core.core.domain import Campaign, ChannelType, CategoryType
from campaigner_core.agents.copywriter.templates import TemplateManager

class ContentGenerator:
    """
    The 'Brain' of the copywriter. 
    Selects templates and generates content (Simulated AI) based on context.
    """
    
    def __init__(self):
        self.template_manager = TemplateManager()
        
    def generate(self, campaign: Campaign) -> Dict[str, Any]:
        # 1. Select Template
        template = self.template_manager.get_template(campaign.channel)
        structure = template["structure"]
        
        # 2. Determine Tone
        tone = self._determine_tone(campaign)
        
        # 3. Generate Logic (Mocking LLM)
        # Context extraction
        ctx = {
            "brand": campaign.brand,
            "category": campaign.category.value,
            "segment": campaign.segment,
            "type": campaign.type.value,
            "comment": campaign.comment or "",
            "subchannel": campaign.subchannel,
            "link": str(campaign.link_commercial)
        }
        
        content = {}
        
        if campaign.channel in [ChannelType.EMAIL, ChannelType.WHATSAPP]:
            content = self._generate_rich_message(campaign, tone, ctx)
        elif campaign.channel in [ChannelType.SMS, ChannelType.PUSH, ChannelType.APP]:
            content = self._generate_short_message(campaign, tone, ctx)
        else:
            # Trigger
            content = self._generate_rich_message(campaign, tone, ctx)

        return {
            "template_used": template["template_id"],
            "tone_applied": tone,
            "final_content": content
        }

    def _determine_tone(self, campaign: Campaign) -> str:
        base_tone = "Professional"
        if campaign.category in [CategoryType.BELLEZA, CategoryType.MODA]:
            base_tone = "Inspirational & Elegant"
        elif campaign.category == CategoryType.ELECTRO:
            base_tone = "Tech-savvy & Direct"
        elif campaign.category == CategoryType.DEPORTES:
            base_tone = "Energetic & Motivating"
            
        if campaign.type.value == "Casa":
            base_tone += " (Internal/Informative)"
        if "urgency" in (campaign.comment or "").lower():
            base_tone += " + Urgent"
            
        return base_tone

    def _generate_rich_message(self, campaign: Campaign, tone: str, ctx: Dict) -> Dict:
        # Simulating LLM
        subject = f"[{ctx['type']}] {ctx['brand']}: Exclusive for {ctx['segment']}"
        if ctx['type'] == "Casa":
            subject = f"Friendly Reminder from {ctx['brand']}"

        body = (f"Hello {ctx['segment']}! We know you love {ctx['category']}. "
                f"That's why {ctx['brand']} has prepared this {ctx['subchannel']} specially for you. "
                f"Context: {ctx['comment']}. Tone: {tone}.")
        
        html_preview = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h1 style="color: #333; margin: 0;">{ctx['brand']}</h1>
                <p style="color: #666; font-size: 14px;">{ctx['category']} | {ctx['type']}</p>
            </div>
            <div style="padding: 20px;">
                <h2 style="color: #444;">{subject}</h2>
                <p style="line-height: 1.6; color: #555;">{body}</p>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{ctx['link']}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">Buy Now</a>
                </div>
            </div>
            <div style="background-color: #eee; padding: 15px; text-align: center; font-size: 12px; color: #888;">
                <p>Sent to {ctx['segment']} • <a href="#">Unsubscribe</a></p>
            </div>
        </div>
        """

        return {
            "subject": subject,
            "preheader": f"Open inside to see {ctx['category']} deals for {ctx['segment']}",
            "title": f"The Best of {ctx['brand']}",
            "body": body,
            "cta_primary": "Shop Now",
            "html_preview": html_preview  # For visualization/download
        }

    def _generate_short_message(self, campaign: Campaign, tone: str, ctx: Dict) -> Dict:
        prefix = f"[{ctx['type']}] " if ctx['type'] == "Casa" else ""
        return {
            "body": f"{prefix}{ctx['brand']}: Hey {ctx['segment']}! Don't miss our {ctx['category']} offers. {ctx['comment']} {ctx['link']}"
        }
