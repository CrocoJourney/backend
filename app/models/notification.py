from datetime import datetime
from pydantic import BaseModel
from tortoise.models import Model
from tortoise import fields

from app.models.user import UserInFront


class Notification(Model):
    id = fields.IntField(pk=True)
    date = fields.DatetimeField(auto_now_add=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="notifications_sent")
    receiver = fields.ForeignKeyField(
        "models.User", related_name="notifications_received")
    subject = fields.CharField(max_length=256)
    content = fields.CharField(max_length=512)
    ressourceUrl = fields.CharField(max_length=256)
    action = fields.BooleanField(default=False)
    buttonUrl1 = fields.CharField(max_length=256, null=True)
    buttonUrl2 = fields.CharField(max_length=256, null=True)
    buttonText1 = fields.CharField(max_length=256, null=True)
    buttonText2 = fields.CharField(max_length=256, null=True)

    class Meta:
        table = "notification"


class NotificationInFront(BaseModel):
    id: int
    date: datetime
    sender: UserInFront | None
    receiver: UserInFront
    ressourceUrl: str
    subject: str
    content: str
    action: bool | None = False
    buttonUrl1: str | None
    buttonUrl2: str | None
    buttonText1: str | None
    buttonText2: str | None
