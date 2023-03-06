from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import parse_obj_as
from app.models.user import UserInFront
from app.models.user import UserInRegister, User
from tortoise.exceptions import IntegrityError
from app.utils.mail import sendWelcomeMail
import aiofiles
from app.models.user import UserInToken
from app.utils.tokens import get_user_in_token

router = APIRouter()


@router.post("/")
async def register(firstname: str = Form(..., description="Prénom de l'utilisateur"),
                   lastname: str = Form(...,
                                        description="Nom de famille de l'utilisateur"),
                   mail: str = Form(..., description="Email de l'utilisateur"),
                   password: str = Form(...,
                                        description="Mot de passe de l'utilisateur"),
                   confirmPassword: str = Form(
                       ..., description="Confirmation du mot de passe de l'utilisateur"),
                   phonenumber: str = Form(...,
                                           description="Numéro de téléphone de l'utilisateur"),
                   car: bool = Form(
                       ..., description="Possède-t-il une voiture ?"),
                   sex: str = Form(..., example="H", description="H ou F"),
                   mailNotification: bool = Form(
                       ..., description="L'utilisateur souhaite-t-il recevoir des notifications par mail ?"),
                   photo: UploadFile = File(..., media_type=["image/png", "image/jpeg"], description="Photo de profil")):
    try:
        # on passe les données du formulaire à pydantic pour les valider avec les validateurs
        form_data = UserInRegister(firstname=firstname, lastname=lastname, mail=mail, password=password,
                                   confirmPassword=confirmPassword, phonenumber=phonenumber, car=car, sex=sex, mailNotification=mailNotification)
        # on crée l'utilisateur dans la base de données
        user = User(**form_data.dict())
        # on hash le mot de passe pour le stocker en base de données
        user.hash = user.get_password_hash(form_data.password)
        if photo is not None:
            # on sauvegarde l'image de profil dans le dossier static de manière asynchrone
            async with aiofiles.open(f"app/static/pictures/{photo.filename}", "wb") as buffer:
                content = await photo.read()
                await buffer.write(content)
            # on met à jour le chemin de l'image de profil dans la base de données
            user.photoPath = photo.filename
        # on sauvegarde l'utilisateur dans la base de données
        await user.save()
        # on envoie un mail de bienvenue attention cette action prend un certain temps ce qui peut ralentir la réponse de l'api
        await sendWelcomeMail(user.mail, user.firstname, user.lastname)
        return {"message": "ok"}
    except IntegrityError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Email already registered")


@ router.get("/")
async def get_users():
    users = await User.all()
    return parse_obj_as(list[UserInFront], users)


@router.put("/")
async def update(user: UserInToken = Depends(get_user_in_token),
                   firstname: str = Form(..., description="Prénom de l'utilisateur"),
                   lastname: str = Form(...,
                                        description="Nom de famille de l'utilisateur"),
                   mail: str = Form(..., description="Email de l'utilisateur"),
                   password: str = Form(...,
                                        description="Mot de passe de l'utilisateur"),
                   confirmPassword: str = Form(
                       ..., description="Confirmation du mot de passe de l'utilisateur"),
                   phonenumber: str = Form(...,
                                           description="Numéro de téléphone de l'utilisateur"),
                   car: bool = Form(
                       ..., description="Possède-t-il une voiture ?"),
                   sex: str = Form(..., example="H", description="H ou F"),
                   mailNotification: bool = Form(
                       ..., description="L'utilisateur souhaite-t-il recevoir des notifications par mail ?"),
                   photo: UploadFile = File(..., media_type=["image/png", "image/jpeg"], description="Photo de profil")):
    try:
        # on passe les données du formulaire à pydantic pour les valider avec les validateurs
        form_data = UserInRegister(firstname=firstname, lastname=lastname, mail=mail, password=password,
                                   confirmPassword=confirmPassword, phonenumber=phonenumber, car=car, sex=sex, mailNotification=mailNotification)
        
        # Récupération de l'utilisateur dans la base de données.
        userInDatabase = await User.get(user)

        # Comparaison des informations fournies avec celles de la BDD.



        return {"message": "ok"}
    except IntegrityError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Email already registered")
