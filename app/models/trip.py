from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel
from datetime import date


class Trip(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=256)
    driver = fields.ForeignKeyField(
        "models.User", related_name="trips_as_driver")
    date = fields.DatetimeField()
    size = fields.IntField()
    departure = fields.ForeignKeyField("models.City", related_name="departure")
    arrival = fields.ForeignKeyField("models.City", related_name="arrival")
    constraints = fields.CharField(max_length=512)
    precisions = fields.CharField(max_length=512)
    price = fields.DecimalField(max_digits=5, decimal_places=2)
    group = fields.ForeignKeyField(
        "models.Group", related_name="trips", null=True)
    private = fields.BooleanField(default=False)
    passengers = fields.ManyToManyField(
        "models.User", related_name="trips_as_passenger")
    candidate = fields.ManyToManyField("models.User", related_name="candidate")

    class Meta:
        table = "trip"


class Step(Model):
    id = fields.IntField(pk=True)
    trip = fields.ForeignKeyField("models.Trip", related_name="steps")
    city = fields.ForeignKeyField("models.City", related_name="trips")
    order = fields.IntField()

    class Meta:
        table = "step"
        unique_together = ("trip", "order")


class StepInPost(BaseModel):
    city_id: int
    order: int


class TripInPost(BaseModel):
    title: str
    size: int
    constraints: str
    precisions: str
    price: float
    private: bool
    steps: list[StepInPost]
    departure: int
    group: int | None
    arrival: int
    date: str
