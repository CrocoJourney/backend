from .test_main import init_db, close_db, client
import pytest


async def registerUser():
    files = [("photo", open('./tests/test.jpg', 'rb'))]
    data = {
        "firstname": "jesuis",
        "lastname": "unebite",
        "mail": "chpchoupinou@gmail.com",
        "password": "jesuisunmotdepasse",
        "confirmPassword": "jesuisunmotdepasse",
        "phonenumber": "0788947064",
        "car": "True",
        "sex": "H",
        "mailNotification": "True"
    }

    response = client.post("/users/", data=data, files=files)
    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"


@pytest.mark.asyncio
async def test_register():
    await init_db()

    # Inscription du nouvel utilisateur.
    await registerUser()

    # Vérification de l'inscription de l'utilisateur.
    response = client.get("/users/")
    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    await close_db()


@pytest.mark.asyncio
async def test_login():
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
    # print("Server response : " + str(response.json))
    assert response.status_code == 200
    await close_db()


@pytest.mark.asyncio
async def test_delete_own_user():
    await init_db()
    # Création de l'utilisateur.
    await registerUser()

    # Connexion en tant qu'utilisateur à supprimer.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tokens = response.json()
    access_token = tokens["access_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Demande de suppression de l'utilisateur.
    response = client.delete(
        "/users/1",
    )

    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    # Confirmation de la suppression de l'utilisateur.
    response = client.get("/users/")
    # print("Server response : " + str(response.json()))
    assert response.json() == []

    await close_db()



@pytest.mark.asyncio
async def test_update_user_profile_password():
    await init_db()

    # Création de l'utilisateur
    await registerUser()

    # Connexion en tant qu'utilisateur de test.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Test de modification du mot de passe.
    # -> Demande de modification.
    response = client.patch("/users/me",
                            json={"password": "newPasswordLol",
                                  "confirmPassword": "newPasswordLol"}
                            )

    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    # -> Vérification des modifications apportées.
    # --> Déconnexion de l'utilisateur.
    response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token}
    )

    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    # --> Reconnexion de l'utilisateur.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "newPasswordLol"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    await close_db()


@pytest.mark.asyncio
async def test_update_user_profile_infos():
    await init_db()
    # Création de l'utilisateur
    await registerUser()

    # Connexion en tant qu'utilisateur de test.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tokens = response.json()
    access_token = tokens["access_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Test de modification des différents champs de l'utilisateur.
    # -> Demande de modification du nom et prénom.
    response = client.patch("/users/me",
                            json={"firstname": "japon",
                                  "lastname": "modifié",
                                  "mail": "maisonmarc7@gmail.com",
                                  "phonenumber": "0000000000",
                                  "car": "False",
                                  "sex": "F",
                                  "mailNotification": "False"
                            }
    )

    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    # --> Vérification des modifications apportées.
    response = client.get("/users/me")

    firstname_changed = response.json()['firstname'] == 'japon'
    lastname_changed = response.json()['lastname'] == 'modifié'
    mail_changed = response.json()['mail'] == 'maisonmarc7@gmail.com'
    tel_changed = response.json()['phonenumber'] == '0000000000'
    sex_changed = response.json()['sex'] == 'F'
    car_changed = response.json()['car'] == False
    mailNotification_changed = response.json()['mailNotification'] == False
    
    # print("Server response : " + str(response.json()))
    assert firstname_changed and lastname_changed and mail_changed and tel_changed and sex_changed and car_changed and mailNotification_changed , "Changes did not occurr !"
    await close_db()






@pytest.mark.asyncio
async def test_update_user_profile_photo():
    pass
    await init_db()
    # Création de l'utilisateur
    await registerUser()

    # Connexion en tant qu'utilisateur de test.
    response = client.post(
        "/auth/login",
        data={"username": "chpchoupinou@gmail.com",
              "password": "jesuisunmotdepasse"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tokens = response.json()
    access_token = tokens["access_token"]
    client.headers["x-crocojourney-authorization"] = f"Bearer {access_token}"

    # Test de modification des différents champs de l'utilisateur.
    # -> Demande de modification de la photo de profil.
    files = [("photo", open('./tests/test2.png', 'rb'))]

    response = client.post(
        "/users/me/profilePicture",
        files=files
    )

    # print("Server response : " + str(response.json))
    assert response.status_code == 200, "Request was not successful !"

    await close_db()
