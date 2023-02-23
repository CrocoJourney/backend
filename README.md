# backend
FastAPI
Tortoise
Redis
PostgreSQL
Docker

# Requis
## Généralités
Le backend a besoin de python 3.11.x et eventuellement de Venv pour installer les dépendances separément de votre environnement python global.
<br>
Le SGDB est postgresql il faut renseigner les variables d'environnement suivantes pour que l'application puisse se connecter à la base de données:
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT

à vous d'installer postgresql sur votre machine et de créer une base de données avec le nom de votre choix.

> Merci de formater votre code avec autopep8
## Installation des dépendances
Pour installer les dépendances du projet il faut se placer à la racine du projet et lancer la commande suivante:
```bash
pip install -r requirements.txt
```
## Tests unitaires
les tests unitaires sont écrits avec pytest et sont dans le dossier tests à vous de configurer votre IDE pour lancer les tests unitaires.

Example avec VSCode fichier settings.json dans le dossier .vscode:
> pas besoin d'écrire soi-même  ce fichier si vous passer par le bouton de configuration dans le menu adequat
```json
{
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```

## Lancement de l'application pour le développement
Pour lancer l'application il faut se placer dans le dossier app et lancer la commande suivante:
```bash
uvicorn main:app --reload
```
## Lancement de l'application pour le déploiement ou l'utilisation par l'équipe front-end
Un fichier docker-compose est fourni pour lancer l'application dans un container docker.
Pour lancer l'application il faut se placer à la racine du projet et lancer la commande suivante:
```bash
docker-compose up -d
```
> attention pour fonctionner l'application a besoin de variables d'environnement, elles peuvent être renseignées dans un fichier .env à la racine du projet