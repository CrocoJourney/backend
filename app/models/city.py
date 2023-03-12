from typing import Optional, Set
from tortoise.models import Model
from tortoise import fields
import json


class City(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=5, unique=True)
    name = fields.CharField(max_length=256)

    async def loadJSON(path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not await City.all().count() == len(data):
                cities = []
                for city in data:
                    cities.append(City(code=city["code"], name=city["nom"]))
                await City.bulk_create(cities)

    class Meta:
        table = "city"
        indexes = ["code", "name"]
