from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (  # Validadores para los formularios
    DataRequired, ValidationError, Email, Regexp, Length, EqualTo
)

from models import User


def name_exists(form, field):
    '''Controla que el usuario no esté ya creado'''

    if User.select().where(User.username == field.data).exists():
        # Raise lanza un error de validación si el usuario ya existe
        raise ValidationError("Ya existe un usuario con ese nombre.")


def email_exists(form, field):
    '''Controla que el eMail no exista ya'''

    if User.select().where(User.email == field.data).exists():
        # Raise lanza un error de validación si el usuario ya existe
        raise ValidationError("Ya existe un usuario con ese eMail")


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$'
            ),
            name_exists
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),  # No puede ser un campo vacío
            Email(),  # Tiene que tener forma de eMail
            email_exists  # No puede repetirse
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo('password2', message='Los password deben coincidir')
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired()  # Solo debe existir
        ]
    )


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
