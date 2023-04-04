from fastapi.testclient import TestClient
import pytest
from tortoise import Tortoise
from app.main import app
from app.models.user import User

# les tests utilisent le module pytest, a toi de configurer ton environnement de dev pour l'utiliser
# pour vscode Antonin peut t'aider

client = TestClient(app)

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
    assert response.status_code == 200, "Request was not successful !"


async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["app.models.user", "app.models.group",
                        "app.models.city", "app.models.trip", "app.models.ban", "app.models.notification", "app.models.review"]})
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()


def test_root():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_async():
    await init_db()
    user = User(password="test", mail="mail.mail.com", salt="haaaaaash",
                firstname="test", lastname="test", phonenumber="0605969659", sex="h", photoPath="/static/img/default.png")
    user.hash = user.get_password_hash("motdepasse")
    await user.save()
    user = await User.get_or_none(mail="mail.mail.com")
    assert user is not None
    await close_db()



