from flask_login import UserMixin


# https://github.com/maxcountryman/flask-login/blob/main/src/flask_login/mixins.py#L1
# К экземпляру можно получить доступ при помощи flask_login.current_user
class User(UserMixin):
    def __init__(self, user):
        self.__row = user

    def get_id(self) -> int:
        # Обязательно возвращает строку
        # Этот id вставляется в сессию, затем оттуда передается в
        # user_loader
        return self.__row.id

    def __getitem__(self, key):
        return getattr(self.__row, key)

    #def is_authenticated(self):
    #    # True, если пользователь авторизован
    #    # Только для таких пользователей будет вызыван обработчик,
    #    # защищенный декоратором login_required
    #    return self.is_active()

    #def is_active(self):
    #    return True

    #def is_anonymous(self):
    #    return False
