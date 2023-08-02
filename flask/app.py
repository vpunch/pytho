# Куки это данные, которые сервер хранит на стороне клиента (например, в
# браузере)
# Браузер добаляет куки в запрос к серверу при помощи заголовка cookie (
# cookie: foo=bar; bar=4)
# Сервер добавляет новые куки при помощи заголовка ответа set-cookie (
# set-cookie: foo=bar)

# Куки можно посмотреть в браузере: Inspect -> Storage -> Cookies
# Куки могут быть отключены в браузере, и сервер об этом не узнает,
# клиент просто не будет вставлять их в запрос

# Куки могут быть постоянными и сессионными. Постоянные указывают, когда
# их удалять (set-cookie: id=1234; expires=<date> или max-age: 10), а
# сессионные удаляются при закрытии браузера (но могут не удаляться,
# если включено автоматическое восстановление сеанса).

# Флаг secure (set-cookie: bah=ban; secure, безопасные куки) говорит о
# том, что куки должны передаваться только, если запрос отправляется по
# HTTPS

# Во Flask flask.session это обертка над куками, где значения шифруются
# при помощи SECRET_KEY. Если вставить куку вручную, то ее значение
# будет храниться в открытом виде, поэтому не стоит так поступать для
# паролей и прочих приватных данных.

import os
import logging
import sys
from typing import Final

import werkzeug
from flask import Flask
import flask_login
from colorama import Back
from datetime import datetime
from flask_migrate import Migrate

from db.adapter import ALCHEMY
from auth.bp import AUTH_BP, LOGIN_MAN
from wsite.bp import WSITE_BP
from api.bp import API_BP
from api.auth import JWT_MAN
from fhandlers import SOCK
from api.ehandlers import handle_error
import rstapp
from doc import SPEC

FORMATTER: Final = logging.Formatter(
        Back.MAGENTA + '%(name)s | %(message)s' + Back.RESET)

HANDLER: Final = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(FORMATTER)
HANDLER.setLevel(logging.DEBUG)

LOGGER: Final = logging.getLogger('main')
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)

MIGRATE: Final = Migrate()

# Регистрация фильтра шаблонизатора

# Функция может принимать больше одного аргумента:
# def my_filter(first, second),
# тогда использовать так: first|filter('second')

#@WSITE_BP.template_filter('restime')  # в аргументе имя фильтра
def restore_time(time: int) -> str:
    return str(datetime.fromtimestamp(time))


def create_app():
    app = rstapp.create_app()

    # Подключение фильтров
    app.add_template_filter(restore_time, 'restime')

    # Подключение модулей
    app.register_blueprint(
        AUTH_BP,
        # Префикс, который неявно добавляется к роутам блюпринта
        url_prefix='/auth'
    )
    app.register_blueprint(WSITE_BP)
    app.register_blueprint(API_BP, url_prefix='/api')

    # Подключение расширений
    LOGIN_MAN.init_app(app)
    ALCHEMY.init_app(app)
    JWT_MAN.init_app(app)
    SOCK.init_app(app)
    MIGRATE.init_app(app, ALCHEMY)
    # Сгенерирует документацию и создаст для нее роуты
    SPEC.register(app)

    return app


if __name__ == '__main__':
    app = create_app()
    db_adapter = app.extensions['db_adapter']

    # Вместо @app.errorhandler(code) этот метод удобней использовать,
    # когда:
    # - используем фабрику приложения (и объект приложения не доступен
    #   глобально),
    # - выносим обработчики ошибок в отдельный модуль
    app.register_error_handler(403, handle_error)

    # Метод для создания тестового (искусственного) запроса
    with app.test_request_context(
        #/path,
        #method='POST'
    ):
        #db_adapter.recreate()

        # Если на пользователе не вызван flask_login.login_user, то
        # здесь будет анонимный пользователей с id=None
        LOGGER.debug(  # flask_login.mixins.AnonymousUserMixin
            'Current user type: %s',
            type(flask_login.current_user._get_current_object())
        )
        LOGGER.debug('id: %s', flask_login.current_user.get_id())

    # Все установленные URL-правила
    url_map: werkzeug.routing.map.Map = app.url_map
    LOGGER.debug(url_map)

    # Параметры конфигурации можно указать здесь, либо в app.config
    app.run(
        #debug=True,  # показывать ошибки в браузере
        processes=1,
        threaded=False
    )
