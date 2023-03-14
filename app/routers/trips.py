from pydantic import parse_obj_as
from tortoise import transactions
from datetime import date
import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.models.trip import Step, Trip, TripInPost
from tortoise import Tortoise

from app.models.user import User, UserInFront, UserInToken
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


@router.get("/{trip_id}")
async def get_trip(trip_id: int, user: UserInToken = Depends(get_user_in_token)):
    trip = await Trip.get_or_none(id=trip_id).prefetch_related(
        "steps__city", "driver", "passengers", "candidates", "departure", "arrival", "group__friends")
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip does not exists")
    userInDB = await User.get_or_none(id=user.id)
    if trip.private is True and trip.driver.id != user.id and userInDB not in trip.group.friends and user.admin is False:
        raise HTTPException(
            status_code=403, detail="You are not allowed to see this trip")
    passengers = [parse_obj_as(UserInFront, passenger)
                  for passenger in trip.passengers]
    candidates = [parse_obj_as(UserInFront, candidate)
                  for candidate in trip.candidates]
    # tortoise to pydantic
    steps = [step.city for step in trip.steps]
    return {
        "id": trip.id,
        "title": trip.title,
        "date": trip.date,
        "size": trip.size,
        "constraints": trip.constraints,
        "precisions": trip.precisions,
        "price": trip.price,
        "private": trip.private,
        "departure": trip.departure,
        "arrival": trip.arrival,
        "steps": steps,
        "driver": parse_obj_as(UserInFront, trip.driver),
        "private": trip.private,
        "group": trip.group.id if trip.private is True else None,
        "passengers": passengers,
        "candidates": candidates,
    }


@router.post("/")
async def create_trips(data: TripInPost, user: UserInToken = Depends(get_user_in_token)):
    driver = await User.get_or_none(id=user.id)
    if driver is None:
        raise HTTPException(status_code=404, detail="User does not exists")
    trip = Trip(driver=driver, title=data.title, size=data.size, constraints=data.constraints, precisions=data.precisions,
                price=data.price, private=data.private, group=data.group, departure_id=data.departure, arrival_id=data.arrival, date=data.date)
    if data.steps is not None:
        steps = [Step(**step) for step in data.steps]
        trip.steps = steps
    await trip.save()
    return trip


@router.delete("/{trip_id}")
async def delete_trip(trip_id: int, user: UserInToken = Depends(get_user_in_token)):
    # supprime le trajet et ses étapes
    trip = await Trip.get_or_none(id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip does not exists")
    if trip.driver_id != user.id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    await trip.delete()
    return {"message": "trip deleted"}


@router.post("/{trip_id}/accept/{passenger_id}")
@transactions.atomic()
async def accept_passenger(trip_id: int, passenger_id: int, user: UserInToken = Depends(get_user_in_token)):
    userInDB = await User.get_or_none(id=user.id)
    passengerInDB = await User.get_or_none(id=passenger_id)
    if userInDB is None:
        raise HTTPException(status_code=404, detail="User does not exists")
    trip = await Trip.get_or_none(id=trip_id).prefetch_related("passengers", "candidates")
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip does not exists")
    if trip.driver_id != user.id:
        raise HTTPException(
            status_code=403, detail="Forbidden this is not your trip")
    if passengerInDB not in trip.passengers:
        raise HTTPException(
            status_code=404, detail="Passenger doesn't request this trip")
    await trip.passengers.add(passengerInDB)
    await trip.candidates.remove(passengerInDB)
    return {"message": "ok"}
