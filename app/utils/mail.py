import os
from fastapi import Request
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER")

templates = Jinja2Templates(directory="static/templates")

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM="crocojourney@antoninrousseau.fr",
    MAIL_PORT=587,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME="CrocoJourney",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER="static/templates",
)


async def sendResetLink(email: str, token: str, firstname: str, lastname: str):
    message = MessageSchema(
        subject="CrocoJourney - Mot de passe",
        recipients=[email],  # List of recipients, as many as you can pass
        template_body={"URL": f"https://crocojourney.antoninrousseau.fr/reset?token={token}",
                       "PRENOM": firstname, "NOM": lastname},
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="reset.html")
    return {"message": "Mail sent"}


async def sendWelcomeMail(email: str, firstname: str, lastname: str):
    message = MessageSchema(
        subject="CrocoJourney - Bienvenue",
        recipients=[email],  # List of recipients, as many as you can pass
        template_body={"PRENOM": firstname, "NOM": lastname,
                       "URL": "https://crocojourney.antoninrousseau.fr"},
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="welcome.html")
    return {"message": "Mail sent"}
