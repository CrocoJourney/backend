from dotenv import load_dotenv
import os
from redis.asyncio.client import Redis

import redis.asyncio as redis

load_dotenv()

ALGORITHM = "HS256"
JWT_SECRET = os.environ.get("JWT_SECRET")

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours


DB_URL = f"postgres://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:5432/{os.environ.get('POSTGRES_DB')}"

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_DB = os.environ.get("REDIS_DB")


async def get_redis() -> Redis:
    return redis.from_url(f"redis://@{REDIS_HOST}:6379/{REDIS_DB}")
