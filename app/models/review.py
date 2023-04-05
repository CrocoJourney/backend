from tortoise.models import Model
from pydantic import BaseModel
from tortoise import fields
from datetime import datetime
from pydantic import BaseModel, validator


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


class ReviewInPost(BaseModel):
    user_rated: int
    trip_rated: int
    rating: int

    @validator("rating")
    def rating_validator(cls, v):
        if not v >= 5 and not v >= 0:
            raise ValueError("Rating must be between 0 and 5")
        return v
    
class ReviewInUpdate(BaseModel):
    rating: int

    