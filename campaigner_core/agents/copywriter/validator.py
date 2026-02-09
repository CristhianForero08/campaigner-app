from datetime import date
from campaigner_core.core.domain import Campaign, ChannelType

class InputValidator:
    """
    Enforces business rules on the Campaign Input.
    """
    
    def validate(self, campaign: Campaign) -> list[str]:
        warnings = []
        
        # 1. Date Coherence
        if campaign.launch_date < campaign.request_date:
            raise ValueError(f"Launch Date ({campaign.launch_date}) cannot be before Request Date ({campaign.request_date})")

        # 2. Image Link Requirement
        visual_channels = [ChannelType.EMAIL, ChannelType.PUSH, ChannelType.APP]
        if campaign.channel in visual_channels and not campaign.link_image:
            warnings.append(f"Channel {campaign.channel.value} usually requires an Image Link for better performance.")
            
        # 3. Approval Check
        if not campaign.ok_to_send:
            warnings.append("Campaign is marked as NOT OK to send. AI generation will proceed as draft.")

        # 4. Total Sends Sanity Check
        if campaign.total_sends > 1000000:
            warnings.append("High volume campaign (>1M). Ensure capacity.")

        return warnings
