from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Email, Message, UserList, UserPublic, Userschema

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

    db_user = User(
        username=user.username, password=user.password, email=user.email
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(session: Session = Depends(get_session), skip: int = 0,
                limit: int = 100):
    users = session.execute(
        select(User).offset(skip).limit(limit)).scalars().all()
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic,
         status_code=HTTPStatus.OK)
def update_user(user_id: int,
                user: Userschema,
                session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    try:
        user_db.email = user.email
        user_db.username = user.username
        user_db.password = user.password

        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        return user_db
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Username or '
            'Email already exists'
        )


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int,
                session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(user_db)
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
