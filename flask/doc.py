from typing import Final

from pydantic import ValidationError
import flask
import spectree as spec

from api._types import ErrorResp

# OpenAPI -- формат описания REST API документации, Swagger --
# инструмент для генерации кода и отображения документации, Redoc --
# более современный UI
DOC_TEMPLATES: Final = spec.config.DEFAULT_PAGE_TEMPLATES

for ui in list(DOC_TEMPLATES):
    if 'swagger' in ui:
        del DOC_TEMPLATES[ui]


def handle_invalid_data(
    request: flask.Request,
    response: flask.Response,
    error: ValidationError,
    view: flask.views.View
):
    # Если ошибки валидации не было, то response будет None
    if response:
        response.data = ErrorResp(
                error='Invalid input data, see documentation').json()


# SpecTree автоматически добавит все определенные методы в документацию
SPEC: Final = spec.SpecTree(
    'flask',     # фреймворк
    path='doc',  # префикс для публикации
    title='Example Flask API',  # заголовок документации
    version='0.1.1',            # версия Flask-приложения
    # Вызывается после валидации, перед вызовом представления
    before=handle_invalid_data
    # Вызывается после вызова представления
    #after=
)
