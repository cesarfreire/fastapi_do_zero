import asyncio
import sys
from http import HTTPStatus
from logging import getLogger

from fastapi import FastAPI

from fastapi_do_zero.routers import auth, todos, users
from fastapi_do_zero.schemas import (
    Message,
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
app = FastAPI(
    title='FastAPI do Zero',
    description='Aplicação do curso de FastAPI do Zero',
    version='0.1.0',
    contact={'name': 'César Freire', 'email': 'iceesar@live.com'},
)

logger = getLogger('uvicorn.error')

app.include_router(users.users_router)
app.include_router(auth.auth_router)
app.include_router(todos.todos_router)


@app.get('/status', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Up!'}
