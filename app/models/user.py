import re
from pydantic import BaseModel, Field, root_validator, validator
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt


class User(Model):
    id = fields.IntField(pk=True)
    mail = fields.CharField(max_length=256, unique=True)
    hash = fields.CharField(max_length=256)
    firstname = fields.CharField(max_length=200)
    lastname = fields.CharField(max_length=200)
    phonenumber = fields.CharField(max_length=10)
    car = fields.BooleanField(default=False)
    sex = fields.CharField(max_length=1)
    admin = fields.BooleanField(default=False)
    mailNotification = fields.BooleanField(default=True)
    photoPath = fields.CharField(max_length=256, default="default.png")

    def get_password_hash(self, password):
        return bcrypt.hash(password)

    def verify_password(self, password):
        return bcrypt.verify(password, self.hash)

    class Meta:
        table = "user"


UserInToken = pydantic_model_creator(
    User, name="UserInToken", include=["id", "admin"])
UserInFront = pydantic_model_creator(
    User, name="UserInFront", exclude=["hash", "phonenumber"])


class UserInRegister(BaseModel):
    mail: str
    password: str
    confirmPassword: str
    firstname: str
    lastname: str
    phonenumber: str
    car: bool = False
    sex: str = Field(..., example="H", description="H or F")
    mailNotification: bool = True

    @validator("sex")
    def sex_validator(cls, v):
        if v not in ["H", "F"]:
            raise ValueError("Sex must be H or F")
        return v

    @validator("password")
    def password_validator(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @validator("phonenumber")
    def phonenumber_validator(cls, v):
        if len(v) != 10:
            raise ValueError("Phone number must be 10 digits")
        return v

    @validator("mail")
    def mail_validator(cls, v):
        if re.match(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", v) is None:
            raise ValueError("Invalid email")
        return v

    @root_validator
    def check_passwords_match(cls, values):
        password = values.get("password")
        confirmPassword = values.get("confirmPassword")
        if password != confirmPassword:
            raise ValueError("Passwords do not match")
        return values
