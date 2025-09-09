from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class Userschema(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Email(BaseModel):
    email: EmailStr
