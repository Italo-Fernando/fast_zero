from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    Email,
    Message,
    Token,
    UserList,
    UserPublic,
    Userschema,
)
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Olá Mundo!'}


# database = []


# @app.get('/html', response_class=HTMLResponse)
# def read_html():
#     return """
#     <html>
#         <head>
#             <title>Exemplo HTML</title>
#         </head>
#         <body>
#             <h1>Olá Mundo!</h1>
#         </body>
#     </html>
#     """


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: Userschema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password
                                        )
    db_user = User(
        username=user.username, password=hashed_password, email=user.email
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(session: Session = Depends(get_session), skip: int = 0,
                limit: int = 100, current_user=Depends(get_current_user)):
    users = session.execute(
        select(User).offset(skip).limit(limit)).scalars().all()
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic,
         status_code=HTTPStatus.OK)
def update_user(user_id: int,
                user: Userschema,
                session: Session = Depends(get_session),
                current_user=Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Username or '
            'Email already exists'
        )


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int,
                session: Session = Depends(get_session),
                current_user=Depends(get_current_user)):
    # user_db = session.scalar(select(User).where(User.id == user_id))
    # if not user_db:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    #     )
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    session.delete(current_user)
    session.commit()
    # session.refresh(user_db) não pode, mesmo que na mesma sessão o objeto foi
    # removido

    return {'message': 'User deleted'}


@app.get('/users/{user_id}/email', response_model=Email)
def read_user_email(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    return {'email': user_db.email}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
