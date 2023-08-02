from typing import Final

import pytest
import flask

from db.adapter import DB_ADAPTER
from app import create_app

USR_DATA: Final = {
    'email': '123456@mail.com',
    'passwd': '123456',
    'sex': 'male'
}


# Фикстура это функция, которая выполняет код перед запуском теста и
# после
# Фикстуры должны указываться в списке параметров функции
@pytest.fixture
def app():
    # Код выполняется перед запуском
    app = create_app()
    app.testing = True

    # Создать контекст приложения
    # app_context
    with app.test_request_context():
        DB_ADAPTER.recreate()

    # Тестовый клиент для выполнения запросов к приложению
    # Данные 
    yield app

    # После
    pass


# TODO написать про scope, conftest, сохранение тестов в разных модулях
@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        DB_ADAPTER.add_user(
                USR_DATA['email'], USR_DATA['passwd'], bool(USR_DATA['sex']))

        return DB_ADAPTER.get_user(email=USR_DATA['email'])


@pytest.fixture
def rtoken(client, user):
    response = client.post('/api/login', json={
        'email': USR_DATA['email'],
        'passwd': USR_DATA['passwd']
    })

    return response.json['refresh_token']


@pytest.fixture
def atoken(client, rtoken):
    response = client.post('/api/refresh', headers={
        'authorization': 'Bearer ' + rtoken
    })

    return response.json['access_token']
