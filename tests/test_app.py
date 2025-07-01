from http import HTTPStatus

from fastapi_do_zero.schemas import UserPublicSchema


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


# Create
def test_create_user_deve_criar_usuario_e_retornar_201(client):
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_create_user_deve_retornar_409_para_usuario_existente(client, user):
    response = client.post(
        '/users',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'new_secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_create_user_deve_retornar_409_para_email_existente(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'new_secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


# Read
def test_read_users_deve_retornar_lista_de_usuarios(client, user):
    user_schema = UserPublicSchema.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_user_deve_retornar_usuario_existente(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_read_user_deve_retornar_404_para_usuario_inexistente(client):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


# Update
def test_update_user_deve_atualizar_usuario_existente(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'new_secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_user_deve_retornar_409_para_usuario_existente(client, user):
    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already exists'
    }


def test_update_user_deve_retornar_404_para_usuario_inexistente(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'alice_not_updated',
            'email': 'alice@example.com',
            'password': 'new_secret',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


# Delete
def test_delete_user_deve_deletar_usuario_existente(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'User deleted successfully'
    }


def test_delete_user_deve_retornar_404_para_usuario_inexistente(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
