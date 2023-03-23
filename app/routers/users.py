import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, ValidationError, parse_obj_as
from app.models.notification import Notification, NotificationInFront
from app.models.user import UserInFront, UserInFrontWithPhone, UserInToken
from app.models.user import UserInRegister, User, UserInUpdate
from tortoise.exceptions import IntegrityError
from app.utils.mail import sendWelcomeMail
import aiofiles
import aiofiles.os

from app.utils.tokens import get_user_in_token
from tortoise import transactions
from fastapi_mail.errors import ConnectionErrors

router = APIRouter()


async def clean_photos(filename: str):
    # on test si un utilisateur utilise encore ce fichier
    user = await User.filter(photoPath=filename).count()
    if user == 0:
        # on supprime le fichier de manière asynchrone
        await aiofiles.os.remove(f"app/static/pictures/{filename}")


@router.post("/")
@transactions.atomic()
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
                       False, description="Possède-t-il une voiture ?"),
                   sex: str = Form(..., example="H", description="H ou F"),
                   mailNotification: bool = Form(
                       ..., description="L'utilisateur souhaite-t-il recevoir des notifications par mail ?"),
                   photo: UploadFile = File(None, media_type=["image/png", "image/jpeg"], description="Photo de profil")):
    try:
        # on passe les données du formulaire à pydantic pour les valider avec les validateurs
        form_data = UserInRegister(firstname=firstname, lastname=lastname, mail=mail, password=password,
                                   confirmPassword=confirmPassword, phonenumber=phonenumber, car=car, sex=sex, mailNotification=mailNotification)
        # on crée l'utilisateur dans la base de données
        user = User(**form_data.dict())
        # on hash le mot de passe pour le stocker en base de données
        user.hash = user.get_password_hash(form_data.password)
        if photo is not None:
            # recupere l'extension du fichier
            extension = photo.filename.split(".")[-1]
            # on vérifie que l'extension est valide
            if extension not in ["png", "jpg", "jpeg", "gif"]:
                raise HTTPException(
                    status_code=400, detail="Invalid file extension")
            # on lit le contenu du fichier
            content = await photo.read()
            # on vérifie que le fichier fait moins de 2Mio
            if len(content) > 2 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, detail="Image too big (max 2Mio)")
            # on génère un hash du contenu de l'image pour éviter les doublons
            hash = hashlib.sha256(content).hexdigest()
            photo.filename = f"{hash}.{extension}"
           # on sauvegarde l'image de profil dans le dossier static de manière asynchrone
            async with aiofiles.open(f"app/static/pictures/{photo.filename}", "wb") as buffer:
                await buffer.write(content)
            # on met à jour le chemin de l'image de profil dans la base de données
            user.photoPath = photo.filename
        else:
            user.photoPath = "default.png"
        # on sauvegarde l'utilisateur dans la base de données
        await user.save()
        # on envoie un mail de bienvenue attention cette action prend un certain temps ce qui peut ralentir la réponse de l'api
        try:
            await sendWelcomeMail(user.mail, user.firstname, user.lastname)
        except ConnectionErrors as e:
            raise HTTPException(
                status_code=500, detail="Internal server error, please contact an administrator")
        return {"message": "ok"}
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already registered")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors()[0]["msg"])


@router.get("/")
async def get_users(user: UserInToken = Depends(get_user_in_token)):
    users = await User.all()
    return parse_obj_as(list[UserInFront], users)


@router.get("/me")
async def get_user(user: UserInToken = Depends(get_user_in_token)):
    user = await User.get(id=user.id)
    # comme cette route n'est accessible que par l'utilisateur connecté on peut lui renvoyer son numéro de téléphone
    return parse_obj_as(UserInFrontWithPhone, user)


@router.get("/{id}")
async def get_user(id: int, user: UserInToken = Depends(get_user_in_token)):
    userInDB = await User.get(id=id)
    return parse_obj_as(UserInFront, userInDB)


@router.delete("/{id}")
async def delete_user(id: int, user: UserInToken = Depends(get_user_in_token)):
    if user.id != id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    await User.filter(id=id).delete()
    return {"message": "ok"}


@router.get("/me/notifications")
async def get_user_notifications(user: UserInToken = Depends(get_user_in_token)):
    notifications = await Notification.filter(receiver_id=user.id).prefetch_related("sender", "receiver").all()
    return notifications


@router.get("/me/notifications/count")
async def get_user_notifications_count(user: UserInToken = Depends(get_user_in_token)):
    count = await Notification.filter(receiver_id=user.id).count()
    return {"count": count}


@router.delete("/me/notifications/{id}")
async def delete_user_notification(id: int, user: UserInToken = Depends(get_user_in_token)):
    notification = await Notification.get_or_none(id=id)
    if notification is None:
        raise HTTPException(
            status_code=404, detail="Notification does not exists")
    if notification.receiver_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await notification.delete()
    return {"message": "ok"}


@router.patch("/me")
async def update(patchedUser: UserInUpdate, user: UserInToken = Depends(get_user_in_token)):
    try:
        userInDatabase = await User.get_or_none(id=user.id)
        if userInDatabase is None:
            raise HTTPException(status_code=404, detail="User does not exists")
        updated_data: dict = patchedUser.dict(exclude_unset=True)

        # Si le mot de passe est renseigné et valide, on le transforme en Hash.
        if 'password' in updated_data and updated_data['password'] is not None:
            updated_data.pop('confirmPassword')
            hash = userInDatabase.get_password_hash(updated_data['password'])
            updated_data.pop('password')
            updated_data['hash'] = hash

        userInDatabase = await userInDatabase.update_from_dict(updated_data)
        await userInDatabase.save()
        return {"message": "ok"}
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post("/me/profilePicture")
async def updateProfilePhoto(background_tasks: BackgroundTasks, photo: UploadFile = File(..., media_type=["image/png", "image/jpeg"], description="Photo de profil"), user: UserInToken = Depends(get_user_in_token)):
    # On récupère l'utilisateur dans la BDD
    user = await User.get_or_none(id=user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exists")
    # recupere l'extension du fichier
    extension = photo.filename.split(".")[-1]
    # on vérifie que l'extension est valide
    if extension not in ["png", "jpg", "jpeg", "gif"]:
        raise HTTPException(
            status_code=400, detail="Invalid file extension")
    # on lit le contenu du fichier
    content = await photo.read()
    # on vérifie que le fichier fait moins de 2Mio
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="Image too big (max 2Mio)")
    # on génère un hash du contenu de l'image pour éviter les doublons
    hash = hashlib.sha256(content).hexdigest()
    photo.filename = f"{hash}.{extension}"
    # on sauvegarde l'image de profil dans le dossier static de manière asynchrone
    async with aiofiles.open(f"app/static/pictures/{photo.filename}", "wb") as buffer:
        await buffer.write(content)
    # on met à jour le chemin de l'image de profil dans la base de données
    anciennePhoto = user.photoPath
    user.photoPath = photo.filename
    await user.save()
    background_tasks.add_task(clean_photos, anciennePhoto)
    return {"message": "ok"}
