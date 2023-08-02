from .conftest import USR_DATA



## Тест это функция, которая начинается с test_
#def test_api_sum(client, atoken):
#    response = client.post(
#        '/api/sum',
#        headers={'authorization': 'Bearer ' + atoken},
#        json={'a': 1, 'b': 2}
#    )
#
#    assert response.json['result'] == 3
#
#
#def test_reg(client):
#    # Контекст будет создан во время запрос
#    # Можем использовать with, чтобы сохранить контекст ПОСЛЕ запроса
#    with client:
#        # url_for здесь не получится использовать, так как нет контекста
#        # data используется для передачи данных формы. multipart/form-data или
#        # application/x-www-urlencoded будет выбрано автоматически. Для
#        # загрузки файла нужно передать объект файла, котрытого в режиме 'rb'.
#        # Изменить определенное имя файла с его типом можно при помощи кортежа:
#        # (picture, 'my-photo.png', 'image/png')
#        # query_string={...}
#        client.post('/auth/reg', data={
#            'email': USR_DATA['email'],
#            'passwd': USR_DATA['passwd'],
#            'passwd_again': USR_DATA['passwd'],
#            'sex': USR_DATA['sex']
#        })
#
#        status, _ = flask.get_flashed_messages(True).pop()
#        assert status == 'success'
#
#
#
#def test_usr_pic(client, user):
#    pic_path = Path('static') / 'flask.png'
#
#    # Для изменения и сохранения сессии
#    with client.session_transaction() as session:
#        session['_user_id'] = user.get_id()
#
#    with client:
#        response = client.post('/upload_usr_pic', data={
#            'picture': pic_path.open('rb')
#        })
#
#        assert response.status_code == 302
#        assert DB_ADAPTER.get_user(id=user.get_id())['picture'] is not None
