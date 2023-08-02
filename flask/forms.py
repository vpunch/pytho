# CSRF (Cross-Site Request Forgery) -- межсайтовая подделка запросов.
# Злоумышленник создает форму на своем сайте, пользователь ее заполняет,
# а запрос отправляется на наш сайт, где пользователь авторизован.
# Либо злоумышленник отправляет картинку на почту, где в src картинке get
# запрос на другой сайт

#XSS
# либо js код на чужом сайте делает к нам запрос, либо js встраивается запросом
# на сайт для вывода в браузер всем клиентам


# Спасает cors, либо в форму можно установить секрутный токен и сравнить его с
# запросом

from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import Email, DataRequired, Length


class LoginForm(FlaskForm):
    # Если не указать текст ошибки, то будет использоваться текст по
    # умолчанию на английском
    email = wtforms.StringField(
        'Email',
        validators=[DataRequired(), Email("Неправильный email")]
    )
    passwd = wtforms.PasswordField(
        'Пароль',
        validators=[DataRequired(), Length(min=4, max=20)]
    )
    need_remem = wtforms.BooleanField('Запомнить меня', default=False)
    submit = wtforms.SubmitField('Подтвердить')

    # wtforms.TextAreaField
    # wtforms.SelectField
    # wtforms.validators.EqualTo(<field_name>, message='') используется
    # для проверки равенства значения из другого поля
