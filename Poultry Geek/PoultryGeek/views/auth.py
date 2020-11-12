from flask import Blueprint

from flask import (render_template, flash, url_for, redirect)
from flask_bcrypt import check_password_hash
from flask_login import (login_user, logout_user, login_required,
                         AnonymousUserMixin)

# App
from PoultryGeek import models
from PoultryGeek import forms

bp = Blueprint("auth", __name__, template_folder='templates', static_folder='static')


# ==============================================================================


# Usuario Invitado
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Invitado'


@bp.route('/register', methods=('GET', 'POST'))  # Métodos HTTP usados aquí
def register():
    """Vista para registrar un usuario"""

    form = forms.RegisterForm()
    if form.validate_on_submit():  # La información del formulario es válida
        # Flash despliega un mensaje después de aceptar el formulario
        # To flash a message with a different category
        flash('¡¡ Usted se ha registrado con éxito !!', 'success')
        models.User.create_user(  # Ahora podemos crear el usuario
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            is_active=False,
            is_admin=False
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Vista iniciar sesión al usuario"""

    # En estas dos primeras lineas, se usa la macro para renderizar el form
    form = forms.LoginForm()  # Se define el formulario
    if form.validate_on_submit():  # Si los datos pasan los validadores...
        try:
            # Query en busca del registro cuyo eMail es el escrito en el form
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:  # No existe ese usuario
            flash('Tu nombre de usuario o contraseña no existe', 'danger')
        else:  # Si el usuario si existe hay que comprobar su contraseña
            if check_password_hash(user.password, form.password.data):
                # Hay que comprobar que el usuario haya sido dado de alta en el
                # sistema por el administrador.
                # print("resultado", models.User.user_is_active(form.email.data))
                if models.User.user_is_active(form.email.data):
                    login_user(user)  # Se loguea con la librería de flask
                    flash('Has iniciado sesión', 'success')
                    return redirect(url_for('evolution'))
                else:
                    flash('No has sido dado de alta. Contacta con p92supeg@uco.es para poder acceder a poultry Geek', 'danger')
                    return redirect(url_for('login'))
            else:
                flash('Tu nombre de usuario o contraseña no existe', 'danger')

    return render_template('login.html', form=form)  # Usa macro para render

@bp.route('/logout')
@login_required  # Puede haber más de un decorador. Este requiere estar logado
def logout():
    """Permite cerrar sesión al usuario"""

    logout_user()  # Termina la sesión de usuario
    flash('Has salido de Poultry Geek', 'success')
    return redirect(url_for('index'))


# ==============================================================================
# TODO