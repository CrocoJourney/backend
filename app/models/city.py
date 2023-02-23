from tortoise.models import Model
from tortoise import fields


class City(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, unique=True)
    soundex = fields.CharField(max_length=256)

    class Meta:
        table = "city"
