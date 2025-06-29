from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_do_zero.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    """
    Esse teste tem 3 etapas (AAA):
    1. Arrange: Preparar o ambiente de teste.
    2. Act: Executar a ação que queremos testar.
    3. Assert: Verificar se o resultado é o esperado.
    """
    # arrange
    client = TestClient(app)

    # act
    response = client.get('/')

    # assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}
