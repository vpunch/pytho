from http import HTTPStatus


def test_api_login_upd(client, rtoken):
    response = client.put('/api/login', headers={
        'authorization': 'Bearer ' + rtoken
    })

    assert response.json['refresh_token'] != rtoken


def test_api_logout(client, rtoken):
    response = client.delete('/api/login', headers={
        'authorization': 'Bearer ' + rtoken
    })

    assert response.status_code == HTTPStatus.OK


def test_atoken_refresh(client, rtoken, atoken):
    response = client.post('/api/refresh', headers={
        'authorization': 'Bearer ' + rtoken
    })

    assert response.json['access_token'] != atoken
