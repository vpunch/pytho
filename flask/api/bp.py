# Части HTTP-запроса:
# - метод,
# - путь,
# - заголовки,
# - тело ответа

# CRUD -- 4 основные функции для работы с данными:
# create -- INSERT (SQL statement), POST (HTTP method),
# read -- SELECT, GET,
# update -- UPDATE, PUT (PATCH),
# delete -- DELETE, DELETE

# PUT определяет новые значения для всех атрибутов объекта (NULL, если
# какие-то не указаны), a PATCH определяет значения только тех
# атрибутов, которые нужно обновить
# Если создается новый объект на конкретной позиции, то считается, что
# он обновляет пустой объект, поэтому такая операция является PUT

# Ответ на запрос тоже содержит тело и заголовки, но также включает код
# статуса обработки

# Некоторые HTTP статус-коды:
# - 100-я -- информация,
# - 200-я -- успех,
# - 300-я -- перенаправление,
# -- 301 -- страница перемещена постоянно,
# -- 302 -- временно,
# - 400-я -- ошибка клиента,
# -- 400 Bad Request -- сервер не может разобрать запрос,
# -- 401 Unauthorized -- требуется авторизация,
# -- 403 Forbidden -- доступ запрещен, и проблема не в авторизации,
# -- 404 NotFound -- ресурс не найден,
# -- 405 Method Not Allowed -- ресурс не имеет запрошенный HTTP-метод,
# -- 413 Content Too Large -- превышен лимит на размер тела,
# -- 422 Unprocessable Content -- сервер разобрал запрос, но в нем
#    неправильные данные,
# - 500-я -- ошибка сервера,
# -- 500 Internal Server Error

from typing import Final
import logging

import werkzeug.exceptions as werk_exc
import flask
from flask import Blueprint
from flask.views import View
from flask_jwt_extended import jwt_required
import celery
import spectree as spec

from db import models as dbmodels
from db import adapter as dbadapter
import _celery.tasks as ctasks
from doc import SPEC
from ._types import MailSend, PostTaskResp, EntityResp
from . import ehandlers as eh

API_BP: Final = Blueprint('api', __name__)

API_BP.register_error_handler(401, eh.handle_401)
#API_BP.register_error_handler(Exception, eh.handle_error)

LOGGER: Final = logging.getLogger('main.' + __name__)
LOGGER.setLevel(logging.DEBUG)


@API_BP.post('/mail/send')
# Декоратор добавит типы входных и выходных данных метода в
# документацию, также добавит десериализацию входных данных и
# сериализацию возвращаемых экземпляров моделей
@SPEC.validate(
    # flask.request.args -validation-> flask.request.context.query
    #query=QueryModel,
    # form -> context.form
    #form=FormModel,
    json=MailSend,
    # Нужно указать типы для каждого статуса
    resp=spec.Response(HTTP_200=PostTaskResp),
    # Эти параметры аналогичны тем, что в конструкторе SpecTree, только
    # для одного обработчика
    #before=,
    #after=
)
# Если будут переданы данные, которые не соответствуют Pydantic-модели,
# обертка вернет ответ со статусом 422, генерация исключения не
# выполнится, поэтому этот случай нельзя обработать в error_handler
def send_mail():
    #body: dict = flask.request.json
    # Доступ к типизированным параметрам
    safe_body: MailSend = flask.request.context.json

    # Отправить сообщение (task message), выполнить задачу в фоне
    result: celery.result.AsyncResult = ctasks.mail_send.delay(
            safe_body.content)

    # Если celery worker не был запущен, то задача просто никогда не
    # будет выполнена
    return PostTaskResp(result_id=result.id)


@API_BP.post('/work')
def work():
    result = ctasks.work.delay()
    return PostTaskResp(result_id=result.id).json()


@API_BP.get('/result/<id_>')
def get_task_res(id_: str):
    result = celery.result.AsyncResult(id_)
    return {'value': result.result if result.ready() else None}


# Class-based (reusable) Views позволяет определить базовый класс с
# разделяемой логикой для представлений

class EntityView(View):
    # View.as_view() создает функцию, которая либо для каждого запроса
    # создает экземпляр этого класса для обработки, либо делает это один
    # раз, если атрибут
    #init_every_request = False

    def __init__(self, model):
        self.__model = model

    #@SPEC.validate(resp=spec.Response(HTTP_200=EntityResp))
    @SPEC.validate(resp=spec.Response(HTTP_200=PostTaskResp))
    def dispatch_request(self, count: int):
        result = ctasks.calc_user.delay()
        return PostTaskResp(result_id=result.id)

        self.set_entities(count)
        result = []

        for entity in self.entities:
            entity_ = {}

            for column in self.__model.__table__.columns:
                entity_[column.name] = getattr(entity, column.name)

            result.append(entity_)

        return EntityResp(result=result)

    def set_entities(self, count: int):
        # self при каждом запросе будет новым
        self.entities = dbadapter.AlchemyAdpt.get_entity(self.__model)[:count]


API_BP.add_url_rule(
    '/db/user/<int:count>',
    view_func=EntityView.as_view('get_users', dbmodels.UserModel)
)

API_BP.add_url_rule(
    '/db/page/<int:count>',
    view_func=EntityView.as_view('get_pages', dbmodels.Page)
)


@API_BP.post('/sum')
@jwt_required()
def sum():
    # Если JSON невалидный, либо content-type не application/json,
    # выбросит исключение с кодом 400 (Bad Request)
    # Использует внутри flask.get_json(), не стоит вызывать его явно
    body = flask.request.json

    return {'result': body['a'] + body['b']}


# Объяснение архитектуры JWT-авторизации:
# https://www.youtube.com/watch?v=mWNN8hpXS-A&t=551s

# 1 Клиент обращается к сервису авторизации с логином и паролем
# 2 Клиенту выдается refresh-токен
#  - Туда может быть включен цифровой отпечаток (версия, имя браузера и
#    т.д), чтобы убедиться, что владелец токена не меняется
#  - Токен можно обменять на другой (без авторизации), чтобы продлить
#    его срок годности
#  - Пользователь может обратиться к сервису авторизации и заблокировать
#    свой токен
#  - Сервис должен хранить состояние всех токенов и помечать неактивные
#  - Если цифровой отпечаток невалидный, либо неактивный токен
#    попытались использовать, то активный токен попадает в блеклист
#  - Refresh-токен нужен клиенту только для работы с сервисом
#    авторизации, для работы с другими сервисами нужен service-токен
# 3 Клиент обращается к серису автизации с запросом действий на
#   вычислительном сервисе и предоставляет свой refresh-токен
# 4 Сервис проверяет refresh-токен и в ответ возвращает access-токен
#  - Он должен жить не дольше 1 дня, значительно меньше, чем refresh,
#    так как его нельзя отозвать
# 5 Пользователь отправляет access-токен в запросе к вычислительному
#   сервису

# Оба типа токенов являются JWT
# JWT состоит из заголовка, нагрузки и цифровой подписи. Нагрзука -- это
# строка с данными (состоянием). Заголовок и нагрузка кодируются в
# base64. Шифрование используется для формирования и проверки подписи.
# https://jwt.io/

# Основная идея JWT-авторизации заключается в том, чтобы вычислительный
# сервис не занимался авторизацией и работал быстрее

# Плюсы перед авторизацией при помощи кук:
# - авторизацией может заниматься отдельный сервер (куки клиента обычно
#   не разделяют между двумя серверами),
# - клиенту не требуется менеджер состояния сессионных данных, ими
#   полностью управляет сервер, а клиент просто хранит.
# Минусы: значительно сложней архитектура.

from . import auth
