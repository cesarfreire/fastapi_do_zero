from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fastapi_do_zero.schemas import (
    Message,
    UserDBSchema,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)

app = FastAPI(
    title='FastAPI do Zero',
    description='Aplicação do curso de FastAPI do Zero',
    version='0.1.0',
    contact={'name': 'César Freire', 'email': 'iceesar@live.com'},
)
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema
)
def create_user(user: UserSchema):
    user_with_id = UserDBSchema(id=len(database) + 1, **user.model_dump())
    database.append(user_with_id)
    return user_with_id


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserListSchema)
def list_users():
    return {'users': database}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def update_user(user_id: int, user: UserSchema):
    user_with_id = UserDBSchema(**user.model_dump(), id=user_id)

    if user_id <= 0 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def delete_user(user_id: int):
    if user_id <= 0 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    user = database.pop(user_id - 1)
    return user


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def read_user(user_id: int):
    if user_id <= 0 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    return database[user_id - 1]
