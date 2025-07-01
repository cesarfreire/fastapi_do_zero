# Token
from http import HTTPStatus

from fastapi_do_zero.security import create_access_token


def test_create_token_deve_retornar_token_para_usuario_existente(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_current_user_nao_existente_deve_retornar_403(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_create_token_deve_retornar_403_para_usuario_inexistente(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'test',
            'password': 'test',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_create_token_deve_retornar_403_para_senha_incorreta(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'wrong_password',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
