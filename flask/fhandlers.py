from typing import Final
from logging import getLogger, DEBUG
import json

from flask_sock import Sock
import _celery.tasks as ctasks
from celery.result import AsyncResult

LOGGER: Final = getLogger('main.' + __name__)
LOGGER.setLevel(DEBUG)

SOCK: Final = Sock()


@SOCK.route('/sock/task/<id_>')
def get_task_res(ws, id_):
    LOGGER.debug('START')
    result = AsyncResult(id_)
    value = result.get()
    LOGGER.debug(value)
    ws.send(value)
