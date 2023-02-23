from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import parse_obj_as
from redis.asyncio.client import Redis
from utils.tokens import check_refresh_token
from utils.tokens import get_data
from utils.db import get_redis
from utils.tokens import UserInToken, generate_tokens, invalidate_refresh_token
from models.user import User

router = APIRouter()


# permet de se connecter en générant un refresh token et un token d'accès
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), redis: Redis = Depends(get_redis)):
    user = await User.get_or_none(mail=form_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return await generate_tokens(parse_obj_as(UserInToken, user), redis)


# permet de se déconnecter proprement en invalidant le refresh token
@router.post("/logout")
async def logout(refresh_token: str, redis: Redis = Depends(get_redis)):
    invalidate_refresh_token(refresh_token, redis)
    return {"message": "ok"}


# permet de rafraichir le token d'accès en utilisant le refresh token ce dernier est aussi renouvelé car il est à usage unique
@router.post("/refresh")
async def refresh(refresh_token: str, redis: Redis = Depends(get_redis)):
    # on vérifie que le refresh token est valide
    if not await check_refresh_token(refresh_token, redis):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    # on récupère les données du token
    user = await get_data(refresh_token)
    # on vérifie que l'utilisateur existe toujours dans la base de données et on récupère ses données
    dbUser = await User.get_or_none(id=user["id"])
    if not dbUser:
        raise HTTPException(status_code=404, detail="User not found")
    # on ne prend que les données qui nous intéressent
    user = parse_obj_as(UserInToken, dbUser)
    # on invalide le refresh token actuel
    await invalidate_refresh_token(refresh_token, redis)
    # on génère un nouveau refresh token et un nouveau token d'accès
    return await generate_tokens(user, redis)
