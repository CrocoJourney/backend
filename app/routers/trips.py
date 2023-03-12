from datetime import date
import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.models.trip import Step, Trip, TripInPost
from tortoise import Tortoise

from app.models.user import User, UserInToken
from app.utils.tokens import get_user_in_token
router = APIRouter()


@router.get("/", description="Date au format YYYY-MM-DD")
async def get_trips(departure: int, arrival: int, date: date = None, user: UserInToken = Depends(get_user_in_token)):
    # trouve les trajets qui passe par la ville de départ et d'arrivée dans le bon sens ou qui ont directement la ville de départ et d'arrivée
    if date is None:
        date = datetime.date.today()
    query = """
        SELECT trip.id as id,title,date,size,price,d.id as departure_id,d.name as departure_name,a.id as arrival,a.name as arrival_name
        FROM trip inner join city a on a.id = trip.arrival_id inner join city d on d.id = trip.departure_id
        WHERE date::date = ($3) and (trip.id IN (
            SELECT trip_id
            FROM step
                INNER JOIN trip ON step.trip_id = trip.id
            WHERE (departure_id = ($1) AND city_id = ($2))
                OR (city_id = ($1) AND arrival_id = ($2))
        )
        OR trip.id IN (
            SELECT id
            FROM trip
            WHERE id IN (
                SELECT s1.trip_id
                FROM step s1
                    JOIN step s2 ON s1.trip_id = s2.trip_id
                    JOIN trip ON s1.trip_id = trip.id
                WHERE s1.city_id = ($1)
                    AND s2.city_id = ($2)
                    AND s1.order < s2.order
            )
        )
        OR (departure_id = ($1) AND arrival_id = ($2)));
    """

    conn = Tortoise.get_connection("default")
    trips = await conn.execute_query_dict(query, values=[departure, arrival, date])
    return trips
