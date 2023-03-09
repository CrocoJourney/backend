import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.models.trip import Step, StepInPost, Trip
from tortoise.expressions import Q, F
from tortoise.functions import Max
from tortoise import models

from app.models.user import User, UserInToken
from app.utils.tokens import get_user_in_token
router = APIRouter()


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
