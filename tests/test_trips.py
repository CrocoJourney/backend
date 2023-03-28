from .test_main import init_db, close_db, registerUser, client
from app.models.city import City

import pytest


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
    assert response.status_code == 200, "Request was not successful !"

    await close_db()
