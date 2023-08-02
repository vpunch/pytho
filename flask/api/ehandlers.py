import logging
from typing import Final

import werkzeug.exceptions as werk_exc
#from flask_jwt_extended.exceptions import NoAuthorizationError

from ._types import ErrorResp

LOGGER: Final = logging.getLogger('main.' + __name__)
LOGGER.setLevel(logging.DEBUG)

# Flask автоматически выбрасывает исключение если:
# - запрос пришел на путь, для которого не определен обработчик (
#   werk_exc.NotFound),
# - если приложение не в режиме DEBUG, исключение не обработано в
#   error_handler и не является экземпляром HTTPException (
#   werk_exc.InternalServerError, оригинальное исключение в
#   http_error.original_exception),
# - запрос пришел на известный путь, но для метода не определен
#   обработчик (werk_exc.MethodNotAllowed)

# - Все исключения для статусов обработки наследуются от HTTPException
# - error_handler может быть определен для любого исключения, а не
#   только для экземпляра HTTPException
# - error_handler должен возвращать ответ на текущий запрос (ответ
#   формируется по тем же правилам, что у представления)
# - У наследников HTTPException определена стандартная страница с
#   описанием статуса, которая будет возвращена в ответе
# - Если исключение 404 генерируется Flask'ом из-за отсутствия роута, то
#   обработчики на уровне блюпринта не рассматриваются
# - Может быть вызван только один error_handler

# Поиск обработчика экземпляра HTTPException выполяется в блюпринте и
# основном модуле, вызывается более специфичный обработчик. Если
# обработчик конкретного статуса есть и в блюпринте, и в основном
# модуле, то приоритет отдается блюпринту.
# Если исключение не является экземпляром HTTPException, то поиск в
# основном модуле будет выполнен только если в блюпринте нет ни одного
# подходящего обработчика


def handle_401(error: werk_exc.Unauthorized):
    LOGGER.debug(error.code)  # 401
    LOGGER.debug(error.name)  # Unauthorized

    # Ответ, который предопределен для исключения (Response из werkzeug)
    response = error.get_response()
    response.content_type = 'application/json'

    response.data = ErrorResp(  # type: ignore[attr-defined]
        error=error.description
    ).json()

    return response


def handle_error(error: Exception):
    LOGGER.debug(error)
    LOGGER.debug(type(error))
    return ErrorResp(error=str(error)).json()


# flask_jwt_extended при инициализации регистрирует свои обработчики
# ошибок на уровне приложения. Можно скорректировать ответ в конфиге
# вместо переопределения.
