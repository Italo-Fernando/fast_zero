from pydantic import BaseModel, EmailStr


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


class UserDB(Userschema):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
