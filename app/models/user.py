from tortoise.models import Model
from tortoise import fields
class User(Model):
    id = fields.IntField(pk=True)
    mail = fields.CharField(max_length=256, unique=True)
    hash = fields.CharField(max_length=256)
    firstname = fields.CharField(max_length=200)
    lastname = fields.CharField(max_length=200)
    phonenumber = fields.CharField(max_length=10)
    voiture = fields.BooleanField(default=False)
    sex = fields.CharField(max_length=1)
    admin = fields.BooleanField(default=False)
    mailNotification = fields.BooleanField(default=True)
    photoPath = fields.CharField(max_length=256)
    class Meta:
        table = "user"