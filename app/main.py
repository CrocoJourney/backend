import datetime
from fastapi import Depends, FastAPI, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from uvicorn import run
from routers import example
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis

from fastapi import HTTPException

tags_metadata = [
    {
        "name": "example",
        "description": "routes d'exemple",
    }
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

app.mount("/static", StaticFiles(directory="static"), name="static")

# importe les routes de l'application
app.include_router(example.router, prefix="/example", tags=["example"])


@app.get("/")
async def root():
    # redirige vers la documentation interactive
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {"status": "ok"}


def create_refresh_token():
    refresh_token = jwt.encode({"exp": datetime.utcnow() + datetime.timedelta(
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token


# permet de lancer le serveur avec python app/main.py pour le dev
# en prod on utilisera gunicorn
if __name__ == '__main__':
    run(app, host='127.0.0.1', port=8000)
