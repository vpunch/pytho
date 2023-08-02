from typing import Annotated, Final

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.orm as sa_orm

# Можно сразу передать приложение в конструктор, можно зарегистрировать
# его позднее, чтобы тестировать приложение с разными конфигурациями
ALCHEMY: Final = SQLAlchemy()

# Плагин вызывает ALCHEMY.session.remove() в @Flask.teardown_appcontext.
# Session создается при помощи scoped_session, поэтому в каждом потоке
# будет свой экземпляр.

# Создаем аннотированный тип (прикрепляем к типу метаданные, которые
# могут быть использованы позднее)
# SQLAlchemy подберет тип столбца в соответствии с указанным типом и
# метаданными
IntPk = Annotated[int, ALCHEMY.mapped_column(primary_key=True)]
Str20 = Annotated[str, ALCHEMY.mapped_column(ALCHEMY.String(20))]
Str20pk = Annotated[
    str,
    ALCHEMY.mapped_column(ALCHEMY.String(20), primary_key=True)
]
# VARCHAR(50) UNIQUE [NOT NULL]
Str50u = Annotated[
    str,
    ALCHEMY.mapped_column(ALCHEMY.String(50), unique=True)
]
Str100 = Annotated[str, ALCHEMY.mapped_column(ALCHEMY.String(100))]
BytesNone = Annotated[bytes, ALCHEMY.mapped_column(default=None)]
UsrFpk = Annotated[
    int,
    ALCHEMY.mapped_column(
        # Первым аргументом передается имя_таблицы.и_столбец
        ALCHEMY.ForeignKey('user.id', ondelete='cascade'),
        primary_key=True
    )
]

# Явные типы столбцов:
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#simple-example


# Описание таблицы в декларативном стиле
# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#step-two-replace-declarative-use-of-schema-column-with-orm-mapped-column
class Page(ALCHEMY.Model):  # type: ignore[name-defined]
    path: sa_orm.Mapped[Str20pk]
    name: sa_orm.Mapped[Str20]
    # По умолчанию SQL-тип будет NOT NULL, но это ограничение можно
    # убрать, поправив хинт
    content: sa_orm.Mapped[str | None]


class UserModel(ALCHEMY.Model):  # type: ignore[name-defined]
    # По умолчанию именем таблицы становится имя модели, где CamelCase
    # заменяется на snake_case
    # Явно задать имя таблицы можно так
    __tablename__ = 'user'

    id: sa_orm.Mapped[IntPk]
    email: sa_orm.Mapped[Str50u]
    passwd: sa_orm.Mapped[Str100]
    time: sa_orm.Mapped[int]
    picture: sa_orm.Mapped[BytesNone | None]

    # Создаем ссылку на объекты из связанной таблицы, но это не
    # обязательно, можно явно объединять таблицы в запросе
    # Если связь многие к одному, то хинт должен быть
    # Mapped[list['Info']]
    info: sa_orm.Mapped['Info'] = sa_orm.relationship(
        # Загрузить объекты через SELECT при обращении к ним (по
        # умолчанию), False -- использовать LEFT JOIN в запросе, чтобы
        # сразу получить данные
        lazy=True,
        # Если создаем двунаправленное отношение (в связанной таблице
        # так же определяется отношение на эту), то нужно указать имя
        # отношения (атрибута) из связанной таблицы
        back_populates='user'
    )


class Info(ALCHEMY.Model):  # type: ignore[name-defined]
    usr_id: sa_orm.Mapped[UsrFpk]
    is_male: sa_orm.Mapped[bool]

    user: sa_orm.Mapped['UserModel'] = sa_orm.relationship(
            back_populates='info')
