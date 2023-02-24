from app.utils.customscheme import CustomOAuth2PasswordBearer
import time
from pydantic import parse_obj_as
from app.models.user import UserInToken
from redis.asyncio.client import Redis
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
import jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer

from app.utils.db import get_redis

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


bearer_scheme = CustomOAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_data(token: str = Depends(bearer_scheme)) -> dict:
    if await is_access_token_banned(token):
        raise HTTPException(status_code=401, detail="Token banned")
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.exceptions.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.exceptions.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    return data


async def check_refresh_token(refresh_token: str, redis: Redis) -> bool:
    """Retourne vrai si le token est présent dans redis donc valide"""
    return await redis.get(refresh_token) is not None


async def create_jwt_token(data: dict, expires_delta: timedelta | None) -> str:
    data = data.copy()
    expire = datetime.utcnow() + expires_delta
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(user: UserInToken, redis: Redis) -> str:
    """Créer un token de rafraichissement et le stocke dans le cache Redis"""
    refresh_token_data = user.dict()
    refresh_token: str = await create_jwt_token(refresh_token_data, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    await redis.setex(refresh_token, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES), user.id)
    return refresh_token


async def create_access_token(user: UserInToken) -> str:
    return await create_jwt_token(user.dict(), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


async def invalidate_refresh_token(refresh_token: str, redis: Redis) -> None:
    """Invalide un token de rafraichissement en le supprimant du cache Redis"""
    await redis.delete(refresh_token)


async def generate_tokens(user: UserInToken, redis: Redis) -> dict:
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user, redis)
    return {"access_token": access_token, "refresh_token": refresh_token}


async def ban_access_token(token: str, redis: Redis) -> None:
    await redis.sadd("banned_tokens", token)
    expiration_time = int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES*60
    # On ajoute le token banni avec son expiration time
    await redis.zadd("zbanned_tokens", {token: expiration_time})
    await remove_expired_banned_tokens(redis)  # On supprime les tokens expirés


# Supprime les tokens bannis expirés du cache Redis cette opération peut etre couteuse en temps
# mais elle est nécessaire pour éviter de garder en mémoire des tokens bannis expirés
# on evite donc de la faire a chaque verification de token
async def remove_expired_banned_tokens(redis: Redis) -> None:
    await redis.zremrangebyscore("zbanned_tokens", 0, time.time())


async def is_access_token_banned(token: str) -> bool:
    redis = await get_redis()
    return await redis.sismember("banned_tokens", token)


async def is_admin(token: str = Depends(bearer_scheme)) -> bool:
    data = await get_data(token)
    return data.get("admin")


async def get_user_in_token(token: str = Depends(bearer_scheme)) -> dict:
    data = await get_data(token)
    return UserInToken(id=data.get("id"), admin=data.get("admin"))


async def admin_required(token: str = Depends(bearer_scheme)) -> None:
    if not await is_admin(token):
        raise HTTPException(status_code=403, detail="Admin required")
