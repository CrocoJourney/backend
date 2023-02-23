from tortoise.models import Model
from tortoise import fields


class Review(Model):
    id = fields.IntField(pk=True)
    date = fields.DatetimeField(auto_now_add=True)
    author = fields.ForeignKeyField("models.User", related_name="reviews")
    rated = fields.ForeignKeyField("models.User", related_name="rated")
    trip = fields.ForeignKeyField("models.Trip", related_name="reviews")
    rating = fields.IntField()

    class Meta:
        table = "review"
        # un utilisateur ne peut pas noter deux fois la même personne pour le même trajet
        unique_together = ("author", "rated", "trip")
