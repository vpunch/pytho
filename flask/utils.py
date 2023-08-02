from functools import wraps

import flask


def with_form(handler, method):
    """Удобный декоратор для обработки запроса из формы."""
    def decorator(proc_path):
        @wraps(proc_path)  # скопировать метаданные функции в другую
        def proc_path_():
            if flask.request.method == method:
                handler()

            return proc_path()

        # APP.route использует имя функции, чтобы вызывать ее из модуля
        # для обработки запроса, поэтому важно сохранить имя
        # оригинальной функции
        #proc_path_.__name__ = proc_path.__name__
        return proc_path_

    return decorator
