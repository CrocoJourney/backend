from .test_main import init_db, close_db, registerUser, client
from app.models.city import City

import pytest


async def prepare_trip():
    private = False
    response = client.post(
        "/trips/",
        json={
            "title": "Un trajet au pif",
            "size": 4,
            "constraints": "Pas de chats autorisés",
            "precisions": "Rendez-vous en face de la mairie",
            "price": 10.0,
            "private": private,
            "steps": [
                {
                    "city_id": "54500",
                    "order": 0
                }
            ],
            "departure": "88500",
            "arrival": "57001",
            "date": "2027-12-21T12:32:25.540Z"
        }
    )
    return response


@pytest.mark.asyncio
async def test_creation_trajet():
    await init_db()
    await City.loadJSON("app/static/communes.json")

    # Inscription du nouvel utilisateur.
    await registerUser()
    # Connexion de l'utilisateur.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Test de création de trajet
    response = await prepare_trip()
    assert response.status_code == 200, "Request was not successful !"

    await close_db()


@pytest.mark.asyncio
async def test_get_trips_with_id():
    await init_db()
    await City.loadJSON("app/static/communes.json")

    # Inscription du nouvel utilisateur.
    await registerUser()
    # Connexion de l'utilisateur.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Test de création de trajet
    response = await prepare_trip()
    assert response.status_code == 200, "Request was not successful !"

    # Vérification de la route de récupération de trajets
    response = client.get(
        "/trips/1"
    )
    assert response.status_code == 200, "Request was not successful !"

    await close_db()
