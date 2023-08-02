from typing import Final
import logging

import flask
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import (
    JWTManager,
    create_refresh_token,
    create_access_token,
    jwt_required,
    get_jwt,           # payload dict of a current token
    get_jwt_identity,  # sub из текущего токена
    decode_token
)
import spectree as spec
import redis

from ._types import (
    ErrorResp,
    SuccessResp,
    PostLogin,
    PostLoginResp,
    PostRefreshResp
)
from doc import SPEC
from .bp import API_BP

LOGGER: Final = logging.getLogger('main.' + __name__)
LOGGER.setLevel(logging.DEBUG)

# sudo docker run -p 6379:6379 -t redis
CACHE: Final = redis.Redis(host='localhost', decode_responses=True)
JWT_MAN: Final = JWTManager()


# Эта функция будет вызываться для каждого валидного токена, чтобы
# проверить, находится ли он в блоклисте
@JWT_MAN.token_in_blocklist_loader
def check_token_block(header: dict, payload: dict):
    if payload['type'] != 'refresh' \
            or CACHE.sismember('tokens', payload['jti']):
        # Если токен в списке актуальных, то он не в блоклисте
        return False

    if payload['fingerp'] != flask.request.user_agent.string:
        # Владелец токена изменился
        LoginMod.del_rtoken()

    for key in CACHE.keys('junk:*'):
        if CACHE.sismember(key, payload['jti']):
            # Если токен устарел, то блокируем актуальный
            LoginMod.del_rtoken(key[5:])
            break

    return True


# POST, потому что создается новый refresh token
@API_BP.post('/login')
@SPEC.validate(
    json=PostLogin,
    resp=spec.Response(HTTP_200=PostLoginResp, HTTP_401=ErrorResp),
    # Тэг будет использован для группировки методов на странице с
    # документацией
    tags=['api', 'auth']
)
def create_rtoken():
    """Получить токен обновления."""
    # Так как несколько разных клиентов могут работать от одного
    # пользователя, будем считать, что сюда отправляет запрос всегда
    # новый клиент
    # Будем хранить все актуальные токены обновления в памяти и разрешим
    # владельцу токена удалить или заменить (обновить) его
    # Если токен у клиента украли, и при попытке удалить или
    # заменить, его не оказалось в базе, удалим связанный актуальный
    # токен, чтобы клиент снова выполнил авторизацию

    # Мы можем хранить токен обновления в куках, так как он должен
    # использоваться только для работы с сервисом авторизации. При этом
    # мы можем не бояться CSRF, так как браузер заблокирует ответ из-за
    # политики CORS. Но с куками не всегда удобно работать на клиенте.

    #1 / 0
    #return werk_exc.NotFound()

    body = flask.request.context.json
    db_adapter = current_app.extensions['db_adapter']
    user = db_adapter.get_user(body.passwd, email=body.email)

    if not user:
        #return ErrorResp(error='User not found'), 401
        # Аргументы после кода будут переданы в конструктор
        # соответствующего исключения
        return flask.abort(401, 'User not found')

    LOGGER.debug(user.get_id())
    return LoginMod.create_rtoken(user.get_id())


class LoginMod(MethodView):
    # Так быстрее и мы сможем сохранять данные между запросами
    init_every_request = False
    # Декораторы, которые будут применяться к каждому методу
    decorators = [jwt_required(refresh=True)]

    def __init__(
        self
        # Здесь можно перечислить аргументы as_view
    ):
        pass

    @SPEC.validate(
        resp=spec.Response(HTTP_200=PostLoginResp),
        tags=['api', 'auth']
    )
    # PUT, потому что вместо старого создается новый refresh token
    def put(
        self
        # Если есть URL-параметры, здесь их нужно указать
    ):
        return self.upd_rtoken()

    @SPEC.validate(
        resp=spec.Response(HTTP_200=SuccessResp),
        tags=['api', 'auth']
    )
    def delete(self):
        self.del_rtoken()
        return SuccessResp()

    @classmethod
    def del_rtoken(cls, token_id: str | None = None):
        if not token_id:
            token_id = get_jwt()['jti']

        assert token_id
        assert CACHE.srem('tokens', token_id) == 1

        junk = CACHE.smembers('junk:' + token_id)
        CACHE.delete('junk:' + token_id)

        if junk:
            junk.add(token_id)

        return junk

    @classmethod
    def create_rtoken(cls, usr_id, junk: set | None = None):
        # Важно делать logout, когда токен больше не нужен, и не делать
        # повторный login вместо обновления. Так злоумышленнику будет
        # тяжелее использовать украденный токен.

        token = create_refresh_token(
            identity=usr_id,
            additional_claims={'fingerp': flask.request.user_agent.string}
        )
        data = decode_token(token)
        # jti -- UUID, присвоенный токену,
        # sub (subject) -- значение identity
        #LOGGER.debug(data)

        token_id = data['jti']
        CACHE.sadd('tokens', token_id)

        if junk:
            CACHE.sadd('junk:' + token_id, *junk)

        return PostLoginResp(refresh_token=token)

    @classmethod
    def upd_rtoken(cls):
        junk = cls.del_rtoken()
        return cls.create_rtoken(get_jwt_identity(), junk)


API_BP.add_url_rule('/login', view_func=LoginMod.as_view('login_mod'))


# POST, потому что создается новый access token
@API_BP.post('/refresh')
# Доступ предоставляется только клиентам с валидным токеном
@jwt_required(
    refresh=True,       # передан refresh token (по умолчанию False)
    #verify_type=False,  # тип токена не важен
    #optional=True       # пустой токен тоже валидный
)
@SPEC.validate(
        resp=spec.Response(HTTP_200=PostRefreshResp), tags=['api', 'auth'])
def create_atoken():
    atoken = create_access_token(identity=get_jwt_identity())
    return PostRefreshResp(access_token=atoken)
