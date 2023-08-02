import secrets
import os
from pathlib import Path

from flask import Flask
from celery import Task, Celery
from db import adapter


def _create_celery(app: Flask):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            # Эта задача будет выполняться в отдельном процессе (или
            # потоке), поэтому нам нужно вставить контекст приложения в
            # стек, чтобы использовать адаптер к базе данных или конфиг
            # приложения
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.name, task_cls=FlaskTask)
    celery.config_from_object(app.config['CELERY_PARAMS'])
    # Чтобы можно было использовать @shared_task
    celery.set_default()

    return celery


def create_app():
    # Первым аргументом передается имя пакета или модуля, которому
    # принадлежит приложение
    # Это имя используется для поиска корневой директории, где лежат ресурсы
    # приложения, поэтому важно указывать корректное значение
    app = Flask(__name__)

    # Обновить конфиг приложения из объекта. Будут прочитаны только
    # **атрибуты** в **верхнем** регистре.
    # Можно передать либо сам объект, либо его имя
    app.config.from_object('config.config')
    app.config.from_object('config._secrets')

    # Секретный ключ необходим для работы сессий, он используется для
    # шифрования данных, которые будут храниться на клиенте
    # 8 случайных байт, каждый из которых отображается в виде 2 16-чисел в
    # строке
    # Секретный ключ должен быть максимально случайным, документация Flask
    # рекомендует использовать этот способ
    app.config['SECRET_KEY'] = secrets.token_hex(8)

    db_name = app.config['DB_NAME']
    # С app.config можно работать как со словарем
    app.config.update({
        'DB_PATH': Path(app.instance_path) / (db_name + '.db'),
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_name}_alchemy.db'
        # Для PostgreSQL эта строка будет
        # postgresql://user:password@localhost/mydatabase
    })

    app.config.from_mapping(
        CELERY_PARAMS=dict(
            broker_url='redis://localhost:6379/0',
            result_backend='redis://localhost:6379/0',
            # Игнорировать reutrn задачи по умолчанию
            task_ignore_result=True
        )
    )

    celery = _create_celery(app)
    # Позволяет получить объект Celery из объекта приложения
    app.extensions['celery'] = celery

    adapter.init(app)
    return app
