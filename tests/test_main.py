from fastapi.testclient import TestClient
from app.main import app

# les tests utilisent le module pytest, a toi de configurer ton environnement de dev pour l'utiliser
# pour vscode Antonin peut t'aider

client = TestClient(app)


# test que l'app est bien accessible
def test_root():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}