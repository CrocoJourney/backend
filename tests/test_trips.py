from .test_main import init_db, close_db, registerUser, client
import pytest


@pytest.mark.asyncio
async def test_creation_trajet():
    await init_db()

    # Inscription du nouvel utilisateur.
    await registerUser()
    # Connexion de l'utilisateur.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print("Server response : " + str(response.json))
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Test de création de trajet
    response = client.post(
        "/trips/",
        json={
            "title": "string",
            "size": 1,
            "constraints": "string",
            "precisions": "string",
            "price": 10.0,
            "private": False,
            "departure": 0,
            "arrival": 0,
            "date": "2023-10-15T17:37:15.181Z"
        }
    )

    assert response.status_code==200 , "Request was not successful !"

    response = client.patch(
        "/trips/1",
        json={}
    )




    await close_db()

