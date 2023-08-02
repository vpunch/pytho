# celery -A _celery.provider worker --loglevel INFO

import smtplib
from email.message import EmailMessage
import time
import json

from celery import shared_task
from flask import current_app

# Celery полезен для выполнения задач в отдельном процессе, чтобы
# избежать ограничения параллельного выполнения GIL
# https://tproger.ru/translations/global-interpreter-lock-guide/

# По умолчанию Celery использует --pool=prefork и создает процессы при
# помощи пакета multiprocessing

# При помощи Celery реализуется архитектура "брокер сообщений"
# Поставщик (producer) отправляет задачу (сообщение) брокеру. Брокер
# организует очереди задач и передает задачи работникам (workers),
# которые их выполняют и кладут результат в специальное хранилище (
# result backend).
# Как вариант, в качестве поставщика и работников использовать Celery,
# в качестве брокера и хранилища результатов -- Redis

# Мы можем разместить работников на разных серверах для масштабирования
# сервиса
# Клиент может периодически отрпавлять запрос к хранилищу результатов,
# чтобы получить результат вычислений, которые запросил у сервиса


# @shared_task позволяет не привязывать задачу к конкретному
# экземпляру Celery
@shared_task(
    # Сохранять состояние задачи, что позволяет использовать AsyncResult
    # для получения результата выполнения
    ignore_result=False
)
def mail_send(content: str) -> bool:
    message = EmailMessage()
    # Авторизованный пользователь обязательно должен владеть этим
    # адресом
    message['From'] = current_app.config['MAIL_FROM']
    message['To'] = current_app.config['MAIL_TO']
    message['Subject'] = 'test message'.title()
    message.set_content(content)

    # Использовать SMTP-сервер провайдера почты. Его ИП в белом листе, и
    # с него можно отправлять письма.

    # Обычно требуется SSL
    # https://yandex.ru/support/mail/mail-clients/others.html#smtpsetting

    # В конце блока менеджер вызовет connection.quit()
    with smtplib.SMTP_SSL(current_app.config['MAIL_SRV'], 465) as connection:
        connection.login(
            current_app.config['MAIL_FROM'],
            current_app.config['MAIL_PASSWD']
        )
        connection.send_message(message)
        return True

    return False


@shared_task
def work() -> bool:
    time.sleep(5)
    return True


@shared_task(ignore_result=False)
def calc_user():
    time.sleep(5)
    return json.dumps({'result': [
        {'content': None, 'name': 'Главная', 'path': '/'}
    ]})
