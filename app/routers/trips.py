from pydantic import parse_obj_as
from tortoise import transactions
from datetime import date, timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.models.notification import Notification
from app.models.trip import Step, Trip, TripInPost, TripInPostModify
from app.models.city import City
from tortoise import Tortoise

from app.models.user import User, UserInFront, UserInToken
from app.models.group import Group
from app.utils.tokens import get_user_in_token
router = APIRouter()


@router.get("/", description="Date au format YYYY-MM-DD")
async def get_trips(departure: str, arrival: str, date: date = None, user: UserInToken = Depends(get_user_in_token)):
    # trouve les trajets qui passe par la ville de départ et d'arrivée dans le bon sens ou qui ont directement la ville de départ et d'arrivée
    if date is not None:
        queryDate = """
            SELECT trip.id as id,driver_id,title,date,size,price,d.code as departure_code,d.name as departure_name,a.code as arrival_code,a.name as arrival_name
            FROM trip inner join city a on a.code = trip.arrival_id inner join city d on d.code = trip.departure_id
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
        trips = await conn.execute_query_dict(queryDate, values=[departure, arrival, date])
        return trips
    else:
        query = """
            SELECT trip.id as id,driver_id,title,date,size,price,d.code as departure_code,d.name as departure_name,a.code as arrival_code,a.name as arrival_name
            FROM trip inner join city a on a.code = trip.arrival_id inner join city d on d.code = trip.departure_id
            WHERE trip.id IN (
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
            OR (departure_id = ($1) AND arrival_id = ($2));
        """
        conn = Tortoise.get_connection("default")
        trips = await conn.execute_query_dict(query, values=[departure, arrival])
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
@transactions.atomic()
async def create_trips(data: TripInPost, user: UserInToken = Depends(get_user_in_token)):
    driver = await User.get_or_none(id=user.id)
    if driver is None:
        raise HTTPException(status_code=404, detail="User does not exists")
    trip = Trip(driver=driver, title=data.title, size=data.size, constraints=data.constraints, precisions=data.precisions,
                price=data.price, private=data.private, group_id=data.group, departure_id=data.departure, arrival_id=data.arrival, date=data.date)
    if data.private is True:
        group = await Group.get_or_none(id=data.group)
        if group is None:
            raise HTTPException(
                status_code=404, detail="Group does not exists")
        if group.owner_id != user.id and user.admin is False:
            raise HTTPException(
                status_code=403, detail="You are not allowed to create this trip")
    else:
        trip.group = None
    await trip.save()
    if data.steps is not None:
        for step in data.steps:
            await Step.create(trip=trip, city_id=step.city_id, order=step.order)
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


@router.post("/{trip_id}/join")
@transactions.atomic()
async def join_trip(trip_id: int, user: UserInToken = Depends(get_user_in_token)):
    # ajoute l'utilisateur au trajet
    userInDB = await User.get_or_none(id=user.id)
    if userInDB is None:
        raise HTTPException(status_code=404, detail="User does not exists")
    trip = await Trip.get_or_none(id=trip_id).prefetch_related("group__friends", "passengers", "candidates", "driver")
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip does not exists")
    if trip.driver_id == user.id:
        raise HTTPException(
            status_code=403, detail="Forbidden this is your trip")
    if trip.private is True and user.id not in trip.group.friends:
        raise HTTPException(
            status_code=403, detail="Forbidden this trip is private and you are not in the group")
    if trip.size == len(trip.passengers):
        raise HTTPException(
            status_code=403, detail="Forbidden this trip is full")
    if userInDB in trip.passengers or userInDB in trip.candidates:
        raise HTTPException(
            status_code=403, detail="Forbidden you are already in this trip")
    await trip.candidates.add(userInDB)
    await Notification.create(sender=userInDB, receiver=trip.driver, action=True,
                              subject="join", content=f"{userInDB.firstname} {userInDB.lastname} veut rejoindre votre trajet :  {trip.title}",
                              ressourceUrl=f"/trips/{trip.id}", buttonUrl1=f"/trips/{trip.id}/accept/{user.id}", buttonUrl2=f"/trips/{trip.id}/refuse/{user.id}",
                              buttonText1="Accept", buttonText2="Refuse")
    return {"message": "ok"}


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
    if passengerInDB not in trip.candidates:
        raise HTTPException(
            status_code=404, detail="Passenger doesn't request this trip")
    await trip.passengers.add(passengerInDB)
    await trip.candidates.remove(passengerInDB)
    return {"message": "ok"}


@router.delete("/{trip_id}/accept/{passenger_id}")
@router.post("/{trip_id}/refuse/{passenger_id}")
@transactions.atomic()
async def refuse_passenger(trip_id: int, passenger_id: int, user: UserInToken = Depends(get_user_in_token)):
    userInDB = await User.get_or_none(id=user.id)
    passengerInDB = await User.get_or_none(id=passenger_id)
    if userInDB is None:
        raise HTTPException(status_code=404, detail="User does not exists")
    if passengerInDB is None:
        raise HTTPException(
            status_code=404, detail="Passenger does not exists")
    trip = await Trip.get_or_none(id=trip_id).prefetch_related("passengers", "candidates")
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip does not exists")
    if trip.driver_id != user.id and user.admin is False:
        raise HTTPException(
            status_code=403, detail="Forbidden this is not your trip")
    if passengerInDB not in trip.candidates:
        raise HTTPException(
            status_code=404, detail="Passenger doesn't request this trip")
    await trip.candidates.remove(passengerInDB)
    return {"message": "ok"}


@router.patch("/{trip_id}", description="Modification du trajet designé par trip_id")
async def change_trip(trip_id: int, data: TripInPostModify, user: UserInToken = Depends(get_user_in_token)):
    userInDB = await User.get_or_none(id=user.id)
    if userInDB is None:
        raise HTTPException(status_code=404, detail="User does not exists.")
    trip = await Trip.get_or_none(id=trip_id).prefetch_related("steps__city", "driver", "passengers", "candidates", "departure", "arrival", "group__friends")
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip does not exists.")
    if user.id != trip.driver.id:
        raise HTTPException(
            status_code=403, detail="Forbidden this is not your trip.")

    # Début des vérifications :
    currentDatePlus24h = datetime.now() + timedelta(hours=24)
    # -> Vérification : Si le trajet est dans moins de 24h, on refuse toute modification.
    if (currentDatePlus24h.astimezone() >= trip.date):
        raise HTTPException(
            status_code=403, detail="Trip is in less than 24h.")

    # -> Vérification : La date de départ modifiée ne doit pas être ramenée à moins de 24h après la date actuelle.
    if (data.date is not None):
        if (currentDatePlus24h.astimezone() >= data.date):
            raise HTTPException(
                status_code=403, detail="New date makes trip depart in less than 24h.")

    # -> Vérification : Si les étapes du trajet ont été modifiées, on fait attention !
    if (data.steps is not None):

        # On supprime les anciennes étapes :
        await Step.filter(trip_id=trip.id).delete()

        # On écrase les anciennes Etapes par les nouvelles Etapes renseignées :
        steps = []
        for s in data.steps:
            steps.append(
                Step(trip_id=trip.id, order=s.order, city_id=s.city_id))
        steps = await Step.bulk_create(steps)
        data.steps.pop()

    # -> Vérification : Si le groupe est marqué comme privé et que le trajet précédent n'est pas déjà privé,
    # On vérifie que l'ID du groupe est renseigné et valide.
    # Si le trajet était privé et devient public, on supprime le champ group_id.
    if (data.private is not None):
        if (data.private and not trip.private):
            # Si pas de group_id donné :
            if (data.group is None):
                raise HTTPException(
                    status_code=400, detail="Trip made private but group_id has not been specified.")
            group = await Group.get_or_none(id=data.group)
            # Si l'ID du groupe ne correspond à aucun groupe :
            if (group is None):
                raise HTTPException(
                    status_code=404, detail="Group provided does not exists.")
            # Si le groupe désigné n'appartient pas à l'utilisateur :
            if (group.owner != user.id):
                raise HTTPException(
                    status_code=403, detail="User is not the owner of the group specified.")
        if (not data.private and trip.private):
            # Si le trajet passe de privé en public, on supprime l'id vers le groupe concerné.
            trip.group = None

    # -> Vérification : Si le nombre de participants du trajet est modifié,
    #  On vérifie que le nombre de places est compatible avec le nombre de personnes acceptées à bord.
    if (data.size is not None):
        passengersAccepted = len(trip.passengers)
        if data.size < passengersAccepted:
            raise HTTPException(
                status_code=403, detail="There are more passengers than places left in this configuration.")

    # Modification du trajet :
    trip.departure = await City.get(code=data.departure)
    trip.arrival = await City.get(code=data.arrival)

    updated_data = data.dict(exclude_unset=True)
    updated_data.pop("departure")
    updated_data.pop("arrival")
    updated_data.pop("steps")

    trip.update_from_dict(updated_data)

    await trip.save()

    return {"message": "ok"}


@router.delete("/trips/{trip_id}/passengers/{passenger_id}")
@transactions.atomic()
async def cancel_participation(trip_id: int, passenger_id: int, user: User = Depends(get_user_in_token)):
    trip = await Trip.get_or_none(id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    passenger = await Step.filter(trip=trip, passenger_id=passenger_id).first()
    if passenger is None:
        raise HTTPException(status_code=404, detail="Passenger not found")

    if passenger.passenger.id != user.id:
        raise HTTPException(
            status_code=403, detail="Only the passenger can cancel their participation")

    await passenger.delete()
    return {"message": "Passenger successfully removed from the trip"}
