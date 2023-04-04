from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel


class Group(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, unique=True)
    owner = fields.ForeignKeyField("models.User", related_name="groups")
    friends = fields.ManyToManyField("models.User", related_name="friends")

    class Meta:
        table = "group"


class GroupInPost(BaseModel):
    name: str
