# Блюпринты нужны, чтобы разбить большое приложение на модули, которые
# легче сопровождать, чтобы сделать архитектуру менее связанной
# Уменьшение зависимостей между модулями позволяет проще вность
# изменения в код

from operator import itemgetter
from typing import Final
import logging

import flask
from flask import Blueprint, current_app
import flask_login

from forms import LoginForm
from user import User
from utils import with_form

LOGGER: Final = logging.getLogger('main.' + __name__)
LOGGER.setLevel(logging.DEBUG)

AUTH_BP: Final = Blueprint(
    'auth',    # имя блюпринта (нужно для ссылки на представления)
    __name__,  # имя импорта, как у конструктора Flask
    # Относительный путь (от пакета блюпринта) к шаблонам блюпринта
    # Шаблоны на уровне приложения имеют приоритет **выше**
    template_folder='templates'
)

# Можно в конструктор передать экземпляр приложения, можно
# зарегистрировать его позднее, чтобы не получить цикл импорта
LOGIN_MAN: Final = flask_login.LoginManager()
# Путь к представлению, на которое будет выполнен редирект из
# @flask_login.login_required
# Если не указать, то будет выброшено исключение 401
# Декоратор добавит GET-параметр next для возврата на страницу после
# авторизаци
# Нужно указать имя блюпринта, если представление принадлежит ему
LOGIN_MAN.login_view = 'auth.handle_login'
# Быстрое сообщение
LOGIN_MAN.login_message = 'Требуется авторизация'
LOGIN_MAN.login_message_category = 'error'


@LOGIN_MAN.user_loader
# usr_id передается в функцию из сессии, тип соответствует User.get_id()
# Если usr_id невалидный, то нужно возвращать None
def load_user(usr_id: int) -> None | User:
    LOGGER.debug('Loading user with the session %s', flask.session)

    db_adapter = current_app.extensions['db_adapter']
    # Функция должна возвращать экземпляр специального класса, который
    # определяет расширение Flask-Login
    return db_adapter.get_user(id=usr_id)
    # Теперь можем получить доступ к текущему пользователю


@AUTH_BP.before_request
def log_before() -> None:
    # Вызывается после before_request приложения
    LOGGER.debug('BP: before request')


@AUTH_BP.after_request
def log_after(response: flask.Response) -> flask.Response:
    # Вызывается перед after_request приложения
    LOGGER.debug('BP: after request')
    return response


@AUTH_BP.teardown_request
def log_teardown(error: BaseException | None) -> None:
    # Вызывается перед @Flask.teardown_request
    # Срабатывает только для запросов, которые попали в блюпринт
    LOGGER.debug('BP: teardown request')


@AUTH_BP.route('/login', methods=['GET', 'POST'])
def handle_login():
    def get_logged_resp(uname: str):
        # flask.url_for() возвращает путь по имени представления
        # Следует использовать всегда, так как имя представления более
        # устойчиво к изменениям
        # Также умеет генерировать путь для представлений с параметрами
        # Требует контекст приложения, так как один и тот же обработчик
        # может использоваться разными приложениями и обслуживать разные
        # пути

        # Будет исключение, если не указать значения параметров
        # представления
        next_path = flask.request.args.get('next') \
                or flask.url_for('wsite.handle_profile', uname=uname)

        # Создать ответ, который просит клиента повторить запрос на
        # другой адрес
        return flask.redirect(
            next_path,
            #status=301
        )

    # С flask.session или flask.request.cookies можно работать как со
    # словарем
    #usr_data = flask.session
    #usr_data = flask.request.cookies

    form = LoginForm()
    LOGGER.debug(flask.request.form)

    db_adapter = current_app.extensions['db_adapter']

    if form.validate_on_submit():  # метод и данные корректные
    #if flask.request.method == 'POST':
        email, passwd = form.email.data, form.passwd.data

        # Если чекбокс активирован, будет отправлено значение атрибута
        # value (по умолчанию 'on'), иначе параметр будет отсутствовать
        need_remem = form.need_remem.data

        if user := db_adapter.get_user(passwd, email=email):
            uname = user['email'].split('@')[0]

            # Явная авторизация через flask.session
            #usr_data['logged'] = uname

            # Авторизация через flask_login
            # User.get_id() запишется в flask.session
            flask_login.login_user(
                user,
                # Не удалять куки, когда браузер закрывается
                remember=bool(need_remem)
            )

            response = get_logged_resp(uname)

            # Явная авторизация через cookies
            # Вставка новой куки
            #response.set_cookie(
            #    'logged',  # key
            #    uname,     # value
            #    #seconds=None
            #)

            return response
        else:
            # Категорию указывать необязательно, по умолчанию 'message'
            flask.flash('Пользователь не найден')

    #if 'logged' in usr_data:
    #    uname = usr_data['logged']
    #if not isinstance(
    #        flask_login.current_user, flask_login.AnonymousUserMixin):
    if flask_login.current_user.is_authenticated:
        uname = flask_login.current_user['email'].split('@')[0]

        return get_logged_resp(uname)

    return flask.render_template(
        'login.html',
        title='авторизация',
        menu=db_adapter.get_menu(),
        form=form
    )


@AUTH_BP.get('/logout')
def handle_logout():
    # Если используется flask.session
    #flask.session.pop('logged', None)

    flask_login.logout_user()

    # flask.redirect можно использовать для редиректа на другой сайт.
    # Для этого нужно указать протокол (https://), либо просто // (по
    # умолчанию будет http).
    # Если строка начинается с /, то это будет абсолютный путь текущего
    # домена, иначе -- относительный (будет добавлен к текущему пути)

    # Точкой перед именем показываем, что нужно представление из
    # текущего блюпринта. Но можно указать явно имя блюпринта (первый
    # аргумент конструктора): auth.handle_login .
    response = flask.redirect(flask.url_for('.handle_login'))

    # Удаление куки
    #response.delete_cookie('logged')

    return response


def _handle_reg_post():
    email, passwd, passwd_again, sex = itemgetter(
            'email', 'passwd', 'passwd_again', 'sex')(flask.request.form)

    if passwd != passwd_again:
        flask.flash('Пароли не совпадают')
        return

    db_adapter = current_app.extensions['db_adapter']
    added, error = db_adapter.add_user(email, passwd, bool(sex))

    if not added:
        flask.flash('Ошибка регистрации', 'error')
    else:
        flask.flash('Зарегистрировано', 'success')


@AUTH_BP.route('/reg', methods=['GET', 'POST'])
@with_form(_handle_reg_post, 'POST')
def handle_reg():
    # Значения, которые можно вернуть для ответа:
    # - value:
    #  - строка -- будет помещена в тело, статус будет 200, content-type
    #    будет text/html,
    #  - словарь или массив -- будет преобразован в JSON,
    # - Response:
    #  - flask.make_response() -- принимает то, что возвращает
    #    представление,
    #  - flask.jsonify() -- сериализует значение в JSON (полезно,
    #    когда значение не является словрем или массивом, например,
    #    константой),
    # - tuple (response = value | Response, если Response, то данные
    #   будут обновлены):
    #  - (response, status, headers),
    #  - (response, status),
    #  - (response, headers),
    # - экземпляр HTTPException (будет именно ответом, а не исключением,
    #   не попадет в error_handler)

    db_adapter = current_app.extensions['db_adapter']
    # Возвращает разметку в виде строки
    html = flask.render_template(
            'reg.html', menu=db_adapter.get_menu())

    return html

    #response = flask.make_response(html)
    # Отобразить страницу текстом
    #response.headers['content-type'] = 'text/plain'
    #return response
    #return response, {'content-type': 'text/plain'}
    #return html, {'content-type': 'text/plain'}
