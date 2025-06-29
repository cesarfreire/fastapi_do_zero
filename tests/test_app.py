from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


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


def test_read_users_deve_retornar_lista_de_usuarios(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'id': 1, 'username': 'alice', 'email': 'alice@example.com'}]
    }


def test_update_user_deve_atualizar_usuario_existente(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'alice_updated',
            'email': 'alice@example.com',
            'password': 'new_secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice_updated',
        'email': 'alice@example.com',
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


def test_read_user_deve_retornar_usuario_existente(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice_updated',
        'email': 'alice@example.com',
    }


def test_read_user_deve_retornar_404_para_usuario_inexistente(client):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_deve_deletar_usuario_existente(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'alice_updated',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_delete_user_deve_retornar_404_para_usuario_inexistente(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
