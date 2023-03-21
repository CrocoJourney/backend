from tortoise import Tortoise
from app.models.city import City
from app.routers import auth, trips, users, groups
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.routers import example
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.utils.db import DB_URL


tags_metadata = [
    {
        "name": "auth",
        "description": "routes d'authentification",
    },
    {
        "name": "users",
        "description": "routes pour les utilisateurs",
    },
    {
        "name": "groups",
        "description": "routes pour les groupes d'utilisateurs / amis",
    },
    {
        "name": "trips",
        "description": "routes sur les trajets",
    },
    {
        "name": "example",
        "description": "routes d'exemple",
    },
]


app = FastAPI(
    title="CrocoJourney API",
    description="API pour le site CrocoJourney",
    contact={
        "name": "Antonin Rousseau",
        "url": "https://antoninrousseau.fr"
    },
    version="0.1.0",
    openapi_tags=tags_metadata
)


@app.on_event("startup")
async def startup():
    # wait for tortoise to be ready
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.models.user", "app.models.group",
                            "app.models.city", "app.models.trip", "app.models.ban", "app.models.notification", "app.models.review"]},
    )
    await Tortoise.generate_schemas()
    # drop table city
    await City.loadJSON("app/static/communes.json")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
current_dir = Path(__file__).parent
app.mount('/static', StaticFiles(directory='app/static'), name='static')

# importe les routes de l'application
app.include_router(example.router, prefix="/example", tags=["example"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(trips.router, prefix="/trips", tags=["trips"])
app.include_router(groups.router, prefix="/groups", tags=["groups"])


@app.get("/")
async def root():
    # redirige vers la documentation interactive
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {"status": "ok"}

Tortoise.init_models(["app.models.user", "app.models.group"], "models")

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.models.user", "app.models.group",
                        "app.models.city", "app.models.trip", "app.models.ban", "app.models.notification", "app.models.review"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
