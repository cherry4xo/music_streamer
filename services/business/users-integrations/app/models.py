from tortoise import fields, Model
from tortoise.contrib.pydantic import pydantic_model_creator
import uuid


class ExternalIdentity(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user_id = fields.UUIDField(null=True)
    provider = fields.CharField(max_length=255)
    provider_user_id = fields.CharField(max_length=255, index=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "external_identities"
        unique_together = (("provider", "provider_user_id"),)
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider}:{self.provider_user_id}"
    
ExternalIdentity_Pydantic = pydantic_model_creator(ExternalIdentity, name="ExternalIdentity")
ExternalIdentityIn_Pydantic = pydantic_model_creator(ExternalIdentity, name="ExternalIdentityIn", exclude_readonly=True)