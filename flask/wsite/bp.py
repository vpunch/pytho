import time
from operator import itemgetter
from pathlib import Path
import logging
from typing import Final
from threading import Thread

import flask
from flask import Blueprint, current_app
import flask_login

from utils import with_form

LOGGER: Final = logging.getLogger('main.' + __name__)
LOGGER.setLevel(logging.DEBUG)

WSITE_BP: Final = Blueprint(
    'wsite',
    __name__,
    static_folder='../static'
    #static_folder='../static/frontend/dist'
)

# В URL лучше не использовать идентификаторы (например, для указания
# статьи), а использовать уникальные имена, которые будут учитываться
# поисковыми системами


@WSITE_BP.before_app_request
def log_before() -> None:
    LOGGER.debug('App: before request')


@WSITE_BP.after_app_request
def log_after(response: flask.Response) -> flask.Response:
    # Не вызывается, если в обработчике возникло исключение
    LOGGER.debug('App: after request')
    return response


# Регистрация обработчика на уровне приложения (APP.teardown_request),
# но через блюпринт
@WSITE_BP.teardown_app_request
def log_teardown(error: BaseException | None) -> None:
    # Вызывается даже, если в обработчике возникло исключение
    # Получит ошибку, если она не была обработана в @errorhandler
    # Нельзя допускать исключения здесь
    # Возвращаемое значение игнорируется
    LOGGER.debug('App: teardown request')


# Обработчик ошибки
# Не стоит обрабатывать ошибки в представлениях, вместо этого
# представления должны вызывать flask.abort(), а перехватывать ошибки
# должны @errorhandler()
# Bluetprint.app_errorhandler() для установки на уровне приложения
@WSITE_BP.errorhandler(404)
def handle_404(error):
    db_adapter = current_app.extensions['db_adapter']
    # Мы перехватили ошибку и **сохранили** статус ответа
    return (
        flask.render_template(
                '404.html', title='ой', menu=db_adapter.get_menu()),
        404  # обязательно нужно указать иначе будет 200 
    )


def _handle_index_req():
    try:
        # Данные GET запроса хранятся в словаре flask.request.args
        name, content = itemgetter('name', 'content')(flask.request.args)
    except KeyError:
        return

    db_adapter = current_app.extensions['db_adapter']

    if db_adapter.add_page(name, content):
        # Flask имеет механизм быстрых сообщений. Это сообщения, которые
        # формирует сервер, и которые показываются клиенту единожды.
        # Сообщения неявно добавляются в session и удаляются оттуда
        # в следующем запросе, либо в текущем, если была вызвана
        # flask.get_flashed_messages().

        # Создать быстрое сообщение
        flask.flash('Страница успешно добавлена', 'success')
    else:
        flask.flash('Ошибка добавления страницы', 'error')


# Один обработчик можем регистрировать для нескольких путей
@WSITE_BP.route('/index')
@WSITE_BP.route('/')
@with_form(_handle_index_req, 'GET')
def handle_index():
    db_adapter = current_app.extensions['db_adapter']
    # Шаблоны берутся из /templates
    # Внутри шаблона можно получить прямой доступ к
    # flask.config/request/session/g
    return flask.render_template(
        'index.html',
        # Далее идут параметры шаблона, которые называются контекстом
        title='про flask',
        menu=db_adapter.get_menu()
    )


# .get() и .post() сокращения для .route(path) и
# .route(path, methods=['POST'])
#@WSITE_BP.get('/<name>')
#def handle_usr_page(name: str):
#    page = DB_ADAPTER.get_page(name)
#
#    if not page:
#        flask.abort(404)
#
#    # Нет разницы для шаблонизатора
#    #menu1 = [{'name': 'foo', 'path': '/bar'}]
#    #MenuItem = namedtuple('MenuItem', ['name', 'path'])
#    #menu2 = [MenuItem('foo', '/bar')]
#
#    return flask.render_template(
#        'usrpage.html',
#        page=page,
#        #menu=menu2
#        menu=DB_ADAPTER.get_menu()
#    )


# /profile и /profile/ -- не одно и то же
@WSITE_BP.get('/profile/<uname>')
@flask_login.login_required  # доступно только авторизованным
def handle_profile(uname: str):
    #usr_data = flask.session
    #usr_data = flask.request.cookies

    #if usr_data.get('logged') != uname:
        # Прерывание обработки запроса
        # Делает raise HTTPException
    #    flask.abort(401)  # unauthorized, доступ запрещен

    db_adapter = current_app.extensions['db_adapter']
    return flask.render_template('profile.html', menu=db_adapter.get_menu())


def _verify_usr_pic(name):
    return name.split('.', 1)[1].lower() == 'png'


#@WSITE_BP.put('/upload_usr_pic')
@WSITE_BP.post('/upload_usr_pic')
def upload_usr_pic():
    # Мы делаем промежуточное представление, чтобы браузер не предлагал
    # повторно отправить данные после обновления страницы

    # Файлы помещаются в files, а не form
    # Доступ к files возможен только когда форма кодировалась в
    # multipart/form-data
    picture = flask.request.files['picture']

    # Следует соблюдать принцип: never trust user input
    # Если бы мы сохраняли файл в файловую систему, используя имя
    # переданного файла, нам нужно бы было применить
    # werkzeug.utils.secure_filename(filename), чтобы преобразовать
    # строку к безопасному имени файла
    # https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/#a-gentle-introduction

    db_adapter = current_app.extensions['db_adapter']

    if _verify_usr_pic(picture.filename):
        db_adapter.set_usr_pic(
                flask_login.current_user.get_id(), picture.read())
    else:
        flask.flash('Поддерживается только PNG')

    return flask.redirect(flask.url_for('auth.handle_login'))


@WSITE_BP.get('/usr_pic/<id_>')
def get_usr_pic(id_):
    db_adapter = current_app.extensions['db_adapter']
    user = db_adapter.get_user(id=id_)
    pic_data = user['picture']

    if not pic_data:
        #default_path = os.path.join('static', 'user.png')
        default_path = Path('static') / 'user.png'
        with current_app.open_resource(default_path) as pic_file:
            pic_data = pic_file.read()

    response = flask.make_response(pic_data)
    response.headers['content-type'] = 'image/png'
    return response


def print_url_for():  # представление для обработки запроса
    path = flask.url_for('.print_usr_for')
    return f'<h1>{path}</h1>'


# Регистрация представления для указанного приложения и url rule
result = WSITE_BP.route('/test/url_for')(print_url_for)
# Просто регистрация, декоратор возвращает ту же функцию
print(result is print_url_for)  # True


# https://flask.palletsprojects.com/en/2.2.x/api/#url-route-registrations
# Сюда попадет: /test/3/3.3
@WSITE_BP.get('/test/<int:id_>/<float:number>')
def print_id_number(id_: int, number: float):
    return f'{id_} {number}'


# Сюда попадет: /test/3.3/3.3
# По умолчанию используется methods=['GET']
@WSITE_BP.route('/test/<path:tail>')
def print_tail(tail: str):
    return tail


# Если правило оканчивается слэшем, а в запросе его нет, то будет
# редирект (/foo -308-> /foo/ & /foo/ -> 200)
# Если правило не оканчивается сэшем, а в запросе он есть, то будет 404
# (/foo/ & /foo -> 404)
# Если правило содержит defaults, а запрос не оканчивается слэшем, то
# будет редирект (/foo -308-> /foo/ + bar=1). Это значит, что правило
# тоже должно оканчиваться слэшем, иначе мэтча не будет.
@WSITE_BP.get('/te/a/', defaults={'b': 1})
def foo(b):
    return f'a {b}'


@WSITE_BP.route('/test/wait')
def wait():
    time.sleep(5)
    return 'ok'


@WSITE_BP.get('/inspect/', defaults={'path': 'index.html'})
@WSITE_BP.get('/inspect/<path:path>')
def handle_inspect(path):
    LOGGER.debug(path)
    return WSITE_BP.send_static_file('frontend/dist/' + path)
    #return WSITE_BP.send_static_file('index.html')


@WSITE_BP.get('/test/counter')
def count():
    # Передача сессионных данных происходит только если меняются
    # значения в словаре session
    # Поэтому нужно внимательней работать со списками и прочими
    # изменяемыми объектами, ссылка на которые не меняется

    # Устанавливать перманентные куки, по умолчанию False
    flask.session.permanent = True

    if 'list' not in flask.session:
        flask.session['list'] = [1, 2, 3]
    else:
        # Можем либо скопировать список, чтобы значение изменилось
        #flask.session['list'] = flask.session['list'][:]

        flask.session['list'][0] += 1
        # Либо явно указать, что сессия изменилась
        #flask.session.modified = True

    return flask.session['list']


@WSITE_BP.get('/test/actx')
def test_appcontext():
    flask.g.foo = 'foo'

    def test():
        LOGGER.debug(flask.request.args)
        #LOGGER.debug(flask.g.foo)

        flask.g.foo = 'bar'
        LOGGER.debug(flask.g.foo)  # bar

    # Просто пушит текущий контекст запроса в новом потоке. Вместе с
    # этим будет создан **новый** контекст приложения, так как в новом
    # потоке стек пуст.
    @flask.copy_current_request_context
    def edit_context():
        test()

    def edit_context_(app: flask.Flask, external_g: Final[flask]):
        with app.app_context():
            LOGGER.debug('External data: %s', external_g.foo)  # foo

            # Здесь нет request context
            # Глобальный объект уже другой, там нет данных, которые
            # добавили снаружи

            test()

    # Если передадим прокси, то не сможем им воспользоваться вне
    # контекста
    thread = Thread(
        args=[
            current_app._get_current_object(),
            flask.g._get_current_object()
        ],
        target=edit_context_
    )
    thread.start()
    thread.join()  # ждать выполнения

    return flask.g.foo  # foo


#with WSITE_BP.test_request_context():
#    # /test/3/3.3
#    print(flask.url_for('.print_id_number', id_=3, number=3.3))


# Пример internal redirect
# Мы можем использовать flask.redirect(), но тогда клиенту придется
# выполнять второй запрос
# Либо мы можем перенаправить запрос внутри приложения, чтобы бытрей
# вернуть ответ
@WSITE_BP.get('/idex')
def test_abot():
    # flask.request (flask.Request) -- прокси на входящий запрос
    # CGI переменные окружения (REQUEST_METHOD, CONTENT_TYPE,
    # QUERY_STRING)
    env = flask.request.environ
    env['PATH_INFO'] = flask.url_for('.test_about')

    # Создать контекст запроса
    req_ctx = WSITE_BP.request_context(env)

    # Для обработки запроса может использоваться цепочка приложений (
    # экземпляров Flask), также один запрос может обрабатываться внутри
    # другого (как в данном примере)

    # Поэтому используются 2 стека: контекстов приложений и запросов. Во
    # Flask 2.2 они реализованы при помощи contextvars.

    # В контексте запроса хранятся данные запроса и сессия. В
    # представлении мы можем ссылаться на текущий запрос и сессию при
    # помощи прокси flask.request и flask.session.
    # В контексте приложения находятся приложение (flask.current_app) и
    # хранилище (flask.g)
    # При создании контекста приложения (app.app_context()), объект приложения добавляется в
    # контекст, а хранилище создается новое
    # https://github.com/pallets/flask/blob/main/src/flask/app.py#L2082

    # В каждом потоке своя пара стеков, поэтому мы не можем использовать
    # прокси в новых потоках, которые создаем во время обработки запроса

    # https://flask.palletsprojects.com/en/2.2.x/reqcontext/?highlight=stack#how-the-context-works
    # https://github.com/pallets/flask/blob/d178653b5f7a5ee2ba15e215ce60caeeb9ed82e1/src/flask/ctx.py#L361
    # Перед добавлением контекста запроса добавляется контекст
    # соответствующего приложения, **если он не на верху** стека
    # После ответа достается контекст запроса. Если он был первым для
    # контекста приложения, то достается и контекст приложения
    # Но если мы добавляем контекст приложения, он добавляется в стек всегда

    # Менеджер вызывает req_ctx.push() и req_ctx.pop() для вставки и
    # удаления из стека
    with req_ctx:
        # Выполнить обработку запроса:
        # - вызвать колбек, зарегистрированный before_request,
        # - если он не вернул значение, вызвать соответствующее
        #   представление,
        # - вызвать колбек на ответе, зарегистрированный after_request
        # - вызывать teardown_*
        response = WSITE_BP.full_dispatch_request()

        # teardown_request()/teardown_appcontext() вызывается, сразу **перед**
        # удалением соответствующего контекста из стека 

        # after_request используется для изменения запроса, поэтому он
        # не будет вызываться, если возникло исключение
        # Если нужно выполнить какую-то операцию независимо от
        # результата обработки, следует использовать teardown_*

    return response
