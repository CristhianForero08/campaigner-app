from typing import Dict, Any
from campaigner_core.core.domain import ChannelType

class TemplateManager:
    """
    Provides base templates for different channels.
    """
    
    def get_template(self, channel: ChannelType) -> Dict[str, Any]:
        if channel in [ChannelType.EMAIL, ChannelType.WHATSAPP]:
            # Trigger uses the same structure as Email/Whatsapp in the request
            return {
                "template_id": f"{channel.value.lower()}_v1",
                "structure": {
                    "subject": "{{subject}}",
                    "preheader": "{{preheader}}",
                    "title": "{{title}}",
                    "body": "{{body}}",
                    "cta_primary": "{{cta}}",
                    # Email specific
                    "html_preview": "{{html_content}}"
                }
            }
        elif channel in [ChannelType.SMS, ChannelType.PUSH, ChannelType.APP]:
            return {
                "template_id": f"{channel.value.lower()}_v1",
                "structure": {
                    "body": "{{body}}"
                }
            }
        else:
            # Fallback for Trigger or others
            return {
                "template_id": "generic_v1",
                "structure": {
                    "subject": "{{subject}}",
                    "preheader": "{{preheader}}",
                    "title": "{{title}}",
                    "body": "{{body}}",
                    "cta_primary": "{{cta}}"
                }
            }
