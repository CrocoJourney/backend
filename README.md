[![Python application](https://github.com/CrocoJourney/backend/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/CrocoJourney/backend/actions/workflows/python-app.yml)
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
Pour lancer l'application il faut se placer à la racine du projet et lancer la commande suivante:
```bash
uvicorn app.main:app --reload --forwarded-allow-ips="*"
```
## Lancement de l'application pour le déploiement ou l'utilisation par l'équipe front-end
Un fichier docker-compose est fourni pour lancer l'application dans un container docker.
Pour lancer l'application il faut se placer à la racine du projet et lancer la commande suivante:

<br>

> En fonction de votre version de docker il se peut que la commande soit docker compose au lieu de docker-compose

```bash
docker-compose up -d --build
```
> Docker va télécharger les images nécessaires et attendre que touts les services soient prêts avant de lancer l'application

<br>

> attention pour fonctionner l'application a besoin de variables d'environnement, elles peuvent être renseignées dans un fichier .env à la racine du projet cet exemple de fichier .env est fourni dans le fichier .env.example

> Docker vous signalera si des variables d'environnement sont manquantes

```bash
POSTGRES_DB=crocojourney
POSTGRES_USER=croco
POSTGRES_PASSWORD=crocojourneypassword
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# openssl rand -hex 32
JWT_SECRET=0c4d7c1505ed2a8958d4037210bad3a1e98a1dccfc2713cc38b71d429ee1d998

REDIS_DB=0
REDIS_HOST=127.0.0.1

ENV=development

# s'inscrire sur sendinblue.com ou utiliser un serveur smtp ex : smtp.gmail.com
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_SERVER=smtp-relay.sendinblue.com
```
