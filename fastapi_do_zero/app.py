from http import HTTPStatus

from fastapi import FastAPI

from fastapi_do_zero.schemas import Message

app = FastAPI(
    title='FastAPI do Zero',
    description='Aplicação do curso de FastAPI do Zero',
    version='0.1.0',
    contact={'name': 'César Freire', 'email': 'iceesar@live.com'},
)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}
