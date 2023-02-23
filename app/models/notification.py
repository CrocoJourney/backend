from tortoise.models import Model
from tortoise import fields


class Notification(Model):
    id = fields.IntField(pk=True)
    date = fields.DatetimeField(auto_now_add=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="notifications_sent")
    receiver = fields.ForeignKeyField(
        "models.User", related_name="notifications_received")
    subject = fields.CharField(max_length=256)
    content = fields.CharField(max_length=512)
    type = fields.ForeignKeyField(
        "models.NotificationType", related_name="notifications")
    buttonUrl1 = fields.CharField(max_length=256)
    buttonUrl2 = fields.CharField(max_length=256)
    buttonText1 = fields.CharField(max_length=256)
    buttonText2 = fields.CharField(max_length=256)

    class Meta:
        table = "notification"


class NotificationType(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256)
    description = fields.CharField(max_length=512)

    class Meta:
        table = "notification_type"
