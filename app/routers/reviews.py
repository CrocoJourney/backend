from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User, UserInToken
from app.models.review import Review, ReviewInPost
from app.models.trip import Trip
from app.utils.tokens import get_user_in_token


router = APIRouter()
