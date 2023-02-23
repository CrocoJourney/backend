from tortoise.models import Model
from tortoise import fields


class Ban(Model):
    id = fields.IntField(pk=True)
    mail = fields.CharField(max_length=256, null=False)

    class Meta:
        table = "ban"
