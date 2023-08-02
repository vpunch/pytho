import datetime
from typing import Final
import secrets

# Максимальный размер файлов (в байтах), которые могут быть загружены в
# приложение. Если его превысить, будет сгенерировано исключение 413.
# Важно ограничить размер, чтобы злоумышленник не перегружал сервер
MAX_CONTENT_LENGTH: Final = 1024 * 1024
DB_NAME: Final = 'example'
DEBUG: Final = True
#DEBUG = False
# Требует session.permanent = True, по умолчанию 31 день
PERMANENT_SESSION_LIFETIME: Final = datetime.timedelta(days=14)
MAIL_SRV: Final = 'smtp.yandex.ru'
# Flask-JWT-Extended
JWT_SECRET_KEY: Final = secrets.token_hex(8)
# Если хотим использовать токены обновления, то нужно добавить
JWT_ACCESS_TOKEN_EXPIRES: Final = datetime.timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES: Final = datetime.timedelta(days=1)
# Можно указать другие локации (например, cookies), либо их список
JWT_TOKEN_LOCATION: Final = 'headers'
JWT_ERROR_MESSAGE_KEY: Final = 'error'
DB_ADAPTER: Final = 'alchemy'
#DB_ADAPTER: Final = 'sqlite'
