# backend
FastAPI
Tortoise

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
