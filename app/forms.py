from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Это поле обязательно"),
        Email(message="Пожалуйста, введите корректный email адрес")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Это поле обязательно")
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message="Это поле обязательно"),
        Length(min=2, max=20, message="Имя должно быть от 2 до 20 символов")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Это поле обязательно"),
        Email(message="Пожалуйста, введите корректный email адрес")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Это поле обязательно"),
        Length(min=6, message="Пароль должен содержать минимум 6 символов")
    ])
    password2 = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message="Это поле обязательно"),
        EqualTo('password', message="Пароли должны совпадать")
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другое имя пользователя')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот email уже зарегистрирован')

class SurveyForm(FlaskForm):
    submit = SubmitField('Завершить оценку')

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        # Динамические поля будут добавлены в routes