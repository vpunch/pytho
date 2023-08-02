# Фласк скорей всего переиспользует потоки, потому что их затратно
# создавать для каждого пользователя
# Когда на сервер приходит новый запрос, и все потоки заняты, он будет
# в ожидании. Обработка предыдущего запроса не будет остановлена, и
# контекст нового запроса не будет помещен в стек.
# Когда предыдущий запрос будет обработан, контекст приложения
# удалится, так как удалился первый контекст запроса в контексте
# приложения. Это значит, что несколько разных пользователей не получат
# доступ к одному контексту приложения.

import sqlite3
from contextlib import closing
import re
from time import time
import os
import logging
from typing import Final, NamedTuple
from pathlib import Path

import flask
# Хэширование нужно базе, поэтому выполняем хэширование в этом модуле
from werkzeug.security import generate_password_hash, check_password_hash
from transliterate import translit
import sqlalchemy.exc as sa_exc

from user import User
from .models import ALCHEMY, Page, UserModel, Info

LOGGER: Final = logging.getLogger('main.' + __name__)
LOGGER.setLevel(logging.DEBUG)

_IMG_NAME_RE: Final = re.compile(
        r'<img\s+([\w="\']+\s+)*src=(?P<name>(\'|")[\w+\.]+\3)')

# К хэшу применяется соль, поэтому для одного и того же пароля каждый
# раз будут получаться разные хэши

# Соль увеличивает комбинаторную сложность подбора пароля методом грубой
# силы, также помогает избежать проблемы, когда клиент вводит уже
# занятый пароль
#LOGGER.debug(generate_password_hash('123'))
#LOGGER.debug(generate_password_hash('123'))


class DBAdapter:
    @classmethod
    def recreate(cls):
        cls._recreate()

        cls.add_page('Главная', None, flask.url_for('wsite.handle_index'))
        cls.add_page('Профиль', None, flask.url_for('auth.handle_login'))

    @classmethod
    def _recreate(cls):
        raise NotImplementedError

    @classmethod
    def get_menu(cls):
        raise NotImplementedError

    @classmethod
    def add_page(cls, name: str, content: str, path: str | None = None):
        raise NotImplementedError

    @classmethod
    def get_page(cls, name: str):
        page = cls._get_page(name)

        if not page:
            return None

        while result := _IMG_NAME_RE.search(page.content):
            name = result.group('name')[1:-1]
            img_path = flask.url_for('static', filename=name)
            page.content = page.content.replace(name, img_path)

        return page

    @classmethod
    def _get_page(cls, name: str):
        raise NotImplementedError

    @classmethod
    def add_user(cls, email: str, passwd: str, is_male: bool):
        raise NotImplementedError

    @classmethod
    def get_user(cls,
                 passwd: str | None = None,
                 **kwargs: object) -> User | None:
        user = cls._get_user(kwargs)

        # Не нужна проверка пароля
        # Либо пароль верный
        if not passwd or user and check_password_hash(user.passwd, passwd):
            return User(user)

        return None

    @classmethod
    def _get_user(cls, kwargs: dict):
        raise NotImplementedError

    @classmethod
    def set_usr_pic(cls, usr_id: str, picture):
        raise NotImplementedError


# PostgreSQL по умолчанию использует изоляцию read commited (блокировка
# при изменении одной записи в разных транзакциях, видимость изменений
# в других транзакциях после их фиксации, моментальная видимость
# изменений в текущей транзакции)
# Лучше сразу закрывать транзакцию при изменении данных, если есть риск
# блокировки с другими пользователями или им требуется скорейшая
# видимость изменений. Иначе это можно сделать позже, например, в
# teardown_appcontext, перед закрытием соединения.
# Если не зафиксировать транзакцию явно, то она будет отменена

# Логическая транзакция открывается при любом execute, даже при чтении
class AlchemyAdpt(DBAdapter):
    @staticmethod
    def _get_transaction():
        """Вернет корневую транзакцию."""
        return ALCHEMY.session.registry().get_transaction()

    @classmethod
    def _recreate(cls):
        ALCHEMY.drop_all()
        ALCHEMY.create_all()

    @classmethod
    def get_menu(cls):
        # Про новый стиль запросов:
        # https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
        stmt = ALCHEMY.select(Page.name, Page.path)

        try:
            result = ALCHEMY.session.execute(stmt)
            rows = result.fetchall()

            # Доступ к значениям по атрибутам
            #LOGGER.debug(rows[0].name)
            # _mapping -> RowMapping, чтобы читать значения также по
            # ключам
            #LOGGER.debug(rows[0]._mapping.name)
            #LOGGER.debug(rows[0]._mapping['name'])
            return rows
        except sa_exc.SQLAlchemyError:
            LOGGER.exception('')
            return []

    @classmethod
    def add_page(cls, name: str, content: str, path: str | None = None):
        # Создаем запись
        # Не обязательно использовать именованные параметры, можно
        # просто передать кортеж значений в конструктор
        page = Page(
            path=path if path else _get_page_path(name),
            name=name,
            content=content
        )

        # session создает логическую транзакцию, фиксирует изменения
        # в объектах, запрашивает соединение у Engine, управляет
        # реальной транзакцией

        # https://ru.stackoverflow.com/a/1505031/546819
        try:
            LOGGER.debug(
                'Транзакция отсутствует до изменений: %s',
                cls._get_transaction()
            )
            ALCHEMY.session.add(page)
            # Для удаления:
            # session.delete(page) или
            # session.execute( delete(Page).where(...) )
            LOGGER.debug(
                    'И неявно создается после: %s', cls._get_transaction())

            # Явно поместить сгенерированные операции в реальную
            # транзакцию
            # Вызывается неявно внутри session.commit()
            #ALCHEMY.session.flush()

            # Закрыть логическую транзакцию фиксацией
            ALCHEMY.session.commit()
        except sa_exc.SQLAlchemyError:
            # Реальная транзакция уже откатилась неявно, нужно откатить
            # логическую транзакцию, чтобы можно было начать новую в
            # той же сессии

            ALCHEMY.session.rollback()
            # Если не выполнить, накопленные операции, которые
            # вставляются session.flush(), не очистятся

            LOGGER.exception('')
            return False

        return True

    @classmethod
    def get_entity(cls, model):
        return ALCHEMY.session.scalars(ALCHEMY.select(model)).all()

    @classmethod
    def _get_page(cls, name: str):
        # Методы для создания соответствующих операторов:
        # ALCHEMY.select/update/delete()

        # stmt: Select
        stmt = ALCHEMY.select(Page).where(Page.path == f'/{name}')
        # Выведет сгенерированный SQL-запрос
        #LOGGER.debug(stmt)

        # execute() или get() вернет ошибку, если таблица в базе не
        # существует (например, из-за того, что базу удалили)
        try:
            # result: Result
            result = ALCHEMY.session.execute(stmt)

            # Вернет экземпляр Page по первичному ключу, либо None
            #return ALCHEMY.session.get(Page, f'/{name}')
        except sa_exc.SQLAlchemyError:
            LOGGER.exception('')
            return None

        # fetchall() вернет list[Row], где Row это NamedTuple (доступ к
        # элементам по индексу или атрибуту) из полей, которые мы
        # передали в select()

        # Для select(Page) Row будет предсталять кортеж из одного
        # элемента: экземпляра Page (row.Page)
        # Для `select(Page.path, Page.name)` Row будет
        # представлять кортеж из значений соответствующих полей (
        # row.path, row.name)

        # fetchone() вернет следующий Row, либо None
        # scalar_one() вернет первый элемент первого Row или
        # sqlalchemy.exc.NoResultFound (наследуется от SQLAlchemyError)
        # scalar_one_or_none() аналогичен, но вернет None, если пусто
        # scalars().all() вернет list первых элементов каждого Row
        #return result.scalar_one()
        return result.scalar_one_or_none()

        # Экземпляр Page не является словарем, к данным можем обращаться
        # только по атрибутам

    @classmethod
    def add_user(cls, email: str, passwd: str, is_male: bool):
        info = Info(is_male=is_male)

        user = UserModel(
            email=email,
            passwd=generate_password_hash(passwd),
            time=int(time()),
            # Можем использовать атрибут relationship, чтобы сразу
            # добавить запись в соседнюю таблицу
            info=info
        )

        try:
            # Явно открываем транзакцию
            # Менеджер контекста самостоятельно ее закроет вызовом
            # session.commit() или session.rollback(), если возникнет
            # исключение
            # Транзакция может быть уже открытой
            with cls._get_transaction() or ALCHEMY.session.begin():
                ALCHEMY.session.add(user)
        except sa_exc.SQLAlchemyError:
            LOGGER.exception('')
            return False, ''

        return True, ''
        # user.id появится **после** комита

    @classmethod
    def _get_user(cls, kwargs: dict):
        # filter_by удобно использовать вместо where как раз в таких
        # случаях, когда поля для фильтрации заранее не известны

        try:
            stmt = (
                ALCHEMY.select(UserModel)
                    # Здесь возниклет исключение, если будет использован
                    # несуществующий атрибут
                    .filter_by(**kwargs)
                    # INNER JOIN
                    #.join(Info, UserModel.id == Info.usr_id)
                    # LEFT JOIN
                    #.outerjoin(Info, UserModel.id == Info.usr_id)
            )
            LOGGER.debug(stmt)

            user = ALCHEMY.session.execute(stmt).scalar_one()
        except sa_exc.SQLAlchemyError:
            LOGGER.exception('')
            return None

        LOGGER.debug(
            'Транзакция открывается даже при SELECT: %s',
            cls._get_transaction()
        )

        return user

    @classmethod
    def set_usr_pic(cls, usr_id: str, picture):
        # https://docs.sqlalchemy.org/en/20/core/operators.html#conjunction-operators
        # Если хотим IN оператор в WHERE: User.name.in_(['foo', 'bar'])
        try:
            ALCHEMY.session.execute(
                ALCHEMY.update(UserModel)
                       .where(UserModel.id == usr_id)
                       .values(picture=picture)
            )
            ALCHEMY.session.commit()
        except sa_exc.SQLAlchemyError as error:
            ALCHEMY.session.rollback()
            LOGGER.exception('')
            return False

        # Для обновления данных также можем получить объект, изменить
        # его данные через атрибуты и вызывать session.commit()
        return True


# SQLite база данных поддерживает множество открытых транзакций чтения,
# но только одну открытую транзакцию записи (в которой изменяются
# данные)
# По умолчанию используется уровень изоляции REFERRED (отложенный).
# Транзакция открывается при первом доступе к базе. Если это было
# чтение, то это транзакция чтения, если записи, то записи. Если внутри
# транзакции чтения были изменены данные, то она повышается до
# транзакции записи.
# Мы должны сразу фиксировать транзакцию, если было изменение днаных,
# чтобы пользователи из других транзакций не получали исключение
# connection.in_transaction -- True, если открыта транзакция записи
class SQLiteAdpt(DBAdapter):
    @staticmethod
    def named_row_convert(cursor, row: tuple):
        fields = [column[0] for column in cursor.description]
        cls = NamedTuple('Row', fields)  # type: ignore[misc]
        return cls(*row)

    @classmethod
    def _recreate(cls):
        db_path = flask.current_app.config['DB_PATH']

        if os.path.isfile(db_path):
            os.remove(db_path)

        cls._create()

    @classmethod
    def get_menu(cls):
        # Функция для получения информации из базы данных
        # Хорошая практика обрабатывать ошибки запросов здесь и
        # возвращать пустой результат

        try:
            # Если нужен всего одни запрос, то лучше использовать
            # соединение
            # Курсор будет создан неявно и возвращен с результатом
            cursor = cls._get_conn().execute('SELECT path, name FROM Page')
        except sqlite3.Error:
            LOGGER.exception('')
            return []

        # Возвращает список строк, которые были получены в результате
        # предыдущего SELECT
        return cursor.fetchall()

    @classmethod
    def add_page(cls, name: str, content: str, path: str | None = None):
        try:
            with cls._get_conn() as connection:
                # Значения пользователя нельзя прямо вставлять в запрос,
                # вместо этого следует использовать параметры, чтобы
                # избежать возможных SQL-инъекций
                # https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
                connection.execute(
                    'INSERT INTO Page VALUES (?, ?, ?)',
                    (path if path else _get_page_path(name), name, content)
                )
        except sqlite3.Error:
            LOGGER.exception('')
            return False

        return True

    @classmethod
    def _get_page(cls, name: str):
        try:
            cursor = cls._get_conn().execute(
                    'SELECT * FROM Page WHERE path = ?', (f'/{name}',))
        except sqlite3.Error:
            LOGGER.exception('')
            return None

        return cursor.fetchone()

    @classmethod
    def add_user(cls, email: str, passwd: str, is_male: bool):
        # Пароль нужно хэшировать, чтобы в случае утечки базы данных
        # было значительно тяжелей получить пароли

        connection = cls._get_conn()

        try:
            # Перед .executescript закрывается открытая транзакция,
            # поэтому ее нужно открывать
            # Принимает только строку с запросом, нельзя передать
            # параметры

            params = dict(
                email=email,
                # Для генерации хорошего хэша пароля используется
                # специальная функция
                passwd=generate_password_hash(passwd),
                time=int(time()),
                is_male=is_male
            )

            connection.execute('''
                INSERT INTO User VALUES (NULL, :email, :passwd, :time, NULL)
            ''', params)

            connection.execute('''
                INSERT INTO Info VALUES (
                    (SELECT id FROM User WHERE email = :email),
                    :is_male
                )
            ''', params)

            connection.commit()
        except sqlite3.IntegrityError:
            return (
                False,
                'Пользователь с указанной электронной почтой уже существует'
            )
        except sqlite3.Error:
            LOGGER.exception('')
            return False, ''
        finally:
            # Если фиксация выполнилась, то ничего не произойдет
            connection.rollback()

        return True, ''

    @classmethod
    def _get_user(cls, kwargs: dict):
        filter_ = ', '.join(map(lambda key: key + ' = ?', kwargs.keys()))

        try:
            cursor = cls._get_conn().execute(
                'SELECT * FROM User WHERE ' + filter_,
                list(kwargs.values())
            )
        except sqlite3.Error:
            LOGGER.exception('')
            return None

        #with closing(cursor):
        return cursor.fetchone()

    @classmethod
    def set_usr_pic(cls, usr_id: str, picture):
        try:
            with cls._get_conn() as connection:
                cursor = connection.execute(
                    'UPDATE User SET picture = ? WHERE id = ?',
                    (picture, usr_id)
                )
        except sqlite3.Error:
            LOGGER.exception('')
            return False

        #cursor.close()
        return True

    @classmethod
    def _connect(cls):
        #:memory:, чтобы создать базу в памяти
        conntection = sqlite3.connect(flask.current_app.config['DB_PATH'])
        # Представлять записи, полученные из базы данных, в виде
        # словаря, а не кортежа
        #conntection.row_factory = sqlite3.Row

        conntection.row_factory = cls.named_row_convert

        return conntection

    @classmethod
    def _get_conn(cls):
        if 'db_conn' not in flask.g:
            flask.g.db_conn = cls._connect()

        return flask.g.db_conn

    @classmethod
    def _create(cls):
        with cls._get_conn() as connection, \
                closing(connection.cursor()) as cursor:
            # __exit__() у connection вызывает self.commit() или
            # self.rollback(), если были исключения, не закрывает
            # соединение, не подавляет исключения

            # Курсор создается для выполнения запросов и чтения
            # полученных данных
            # Курсор можно использовать повторно (несколько раз
            # вызывать .execute()), но данные предыдущего запроса
            # будут очищены
            # Курсор тоже следует закрывать в конце использования

            # Открыть файл относительно app.root_path
            # Открыть можно только для чтения
            # По умолчанию открывает на чтение в бинарном режиме
            # Есть такой же метод для блюпринта
            schema = flask.current_app.open_resource(
                Path('db') / 'schema.sql',
                mode='r'
            )

            # Flask/Blueprint.root_path возвращает **абсолютный** путь к
            # пакету приложения/блюпринта (в котором модуль с
            # определением приложения/блюпринта)

            # Имеется Flask.open_instance_resource(), которая открывает
            # путь относительно Flask.instance_path
            # instance_path содержит абсолютный путь к директории с
            # файлами, которые генерирует приложение. Эта директория
            # может находиться где угодно, но по умолчанию:
            # Flask.root_path / 'instance'

            with schema:
                cursor.executescript(schema.read())


def _close_conn(error: BaseException | None) -> None:
    if 'db_conn' in flask.g:
        flask.g.db_conn.close()
        LOGGER.info('DB connection closed')


def _get_page_path(name: str):
    return '/' + translit(name, 'ru', reversed=True)


def init(app: flask.Flask):
    match app.config['DB_ADAPTER']:
        case 'alchemy':
            app.extensions['db_adapter'] = AlchemyAdpt
            app.teardown_appcontext(_close_conn)
        case 'sqlite':
            app.extensions['db_adapter'] = SQLiteAdpt
        case _:
            raise ValueError
