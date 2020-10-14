from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, FileField, DateField,
    IntegerField
)
from wtforms.validators import (  # Validadores para los formularios
    DataRequired, ValidationError, Email, Regexp, Length, EqualTo
)

import models

def name_exists(form, field):
    """Controla que el usuario no esté ya creado"""

    if models.User.select().where(models.User.username == field.data).exists():
        # Raise lanza un error de validación si el usuario ya existe
        raise ValidationError("Ya existe un usuario con ese nombre.")


def email_exists(form, field):
    """Controla que el eMail no exista ya"""

    if models.User.select().where(models.User.email == field.data).exists():
        # Raise lanza un error de validación si el usuario ya existe
        raise ValidationError("Ya existe un usuario con ese eMail")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==============================================================================

# Cada campo en las clases, significa un campo en el HTML


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


class PostForm(FlaskForm):
    """Formulario para el contenido del Post. Hace falta escribir algo"""

    content = TextAreaField('Qué piensas', validators=[DataRequired()])


class LoadDataForm(FlaskForm):
    """Formulario para introducir datos a partir de una tabla"""

    file = FileField('Selecciona un fichero', validators=[DataRequired()])

class SearchForm(FlaskForm):
    """Formulario para la busqueda en la sección de analisis de datos"""

    num = IntegerField('num', validators=[DataRequired()])

    desde = DateField("desde", format="%d-%m-%Y", validators=[DataRequired()])
    hasta = DateField("hasta", format="%d-%m-%Y", validators=[DataRequired()])

    # email = StringField('Email', validators=[DataRequired(), Email()])
    # password = PasswordField('Password', validators=[DataRequired()])
