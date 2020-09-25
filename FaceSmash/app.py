# g es un objeto global donde guardar la info de la app que queramos
# Como es global, es accesible en todo el proyecto.
# Para la ocasión, se usará para los métodos before y after request
# flash -> desplegar un mensaje después de la siguiente petición
# url_for es para generar una url a un cierto endpoint
from flask import Flask, g, render_template, flash, url_for, redirect
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)  # A partir de la vista de Post
from flask_bcrypt import check_password_hash

import models
import forms  # LoginForm, RegisterForm

DEBUG = True  # Mayúsculas indica que es global (por convenio)
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)  # Se instancia la aplicación
app.secret_key = 'kaAsn4oeiASDL13JKHsdrjv<sklnv´lsjdAsCaxcAv'  # Llave Secreta.
# Se utiliza entre otras cosas para diferenciar esta app de otras en la web.
# Usar cualquier cadena, cuyos caracteres sean variados y aleatorios

login_manager = LoginManager()  # Se crea una variable donde alojarlo
login_manager.init_app(app)  # Login manager va a controlar las sesiones de app

# Qué vista mostrar cuando el usuario quiera loguearse o sea redirigido
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    """Método para cargar el usuario qué esté logueado"""

    try:
        # Devuelve el registro del usuario que tenga el mismo name que buscamos
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


# Por convenio se usan (y se nombran así) los siguientes métodos:
# El nombre de los métodos es opcional.
# Lo que hace que tengan la característica especial deseada es el decorador
# Un decorador es una función que envuelven a otras funciones. Empiezan por @


@app.before_request  # Decorador
def before_request():
    """Método que se ejecuta antes de hacer una petición (request) a la bbdd.
    - Establece las conexiones a la bbdd
    """

    # Esta función verifica que el objeto g no tenga ya definido el atributo db
    # Esto evita errores al tratar de volver a definirlo.
    # if not hasattr(g, 'db'):
    g.db = models.DATABASE  # La bbdd es la definida en el archivo models

    # if not hasattr(g, 'user'):
    g.user = current_user  # Usuario actual definido en flask

    if g.db.is_closed():
        g.db.connect()


@app.after_request
def after_request(response):  # response es la respuesta a la petición
    """Método que se ejecuta después de hacer una petición (request) a la bbdd.
    - Cierra las conexiones con la bbdd
    """

    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))  # Métodos HTTP usados aquí
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
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Vista iniciar sesión al usuario"""

    # En estas dos primeras lineas, se usa la macro para renderizar el form
    form = forms.LoginForm()  # Se define el formulario
    if form.validate_on_submit():  # Si los datos pasan los validadores...
        try:
            # Query en busca del registro cuyo eMail es el escrito en el form
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:  # No existe ese usuario
            flash('Tu nombre de usuario o contraseña no existe', 'error')
        else:  # Si el usuario si existe hay que comprobar su contraseña
            if check_password_hash(user.password, form.password.data):
                login_user(user)  # Se loguea con la librería de flask
                flash('Has iniciado sesión', 'success')
                return redirect(url_for('index'))
            else:
                flash('Tu nombre de usuario o contraseña no existe', 'error')

    return render_template('login.html', form=form)  # Usa macro para render


@app.route('/logout')
@login_required  # Puede haber más de un decorador. Este requiere estar logado
def logout():
    """Permite cerrar sesión al usuario"""

    logout_user()  # Termina la sesión de usuario
    flash('Has salido de FaceSmash', 'success')
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
def post():
    """Permite crear nuevos post usando el formulario correspondiente"""

    form = forms.PostForm()

    # Se ejecuta el método si la validación al hacer click en el HTML es válida
    if form.validate_on_submit():

        # Se crea un nuevo post en la tabla
        # _get_current_object() te da el objeto real al que está referenciando
        # Esto lo tiene que hacer porque current_user es un proxy.
        # models.Post.create(user=g.user._get_current_object(),
        # models.Post.create(user=g.user,
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())  # Quita espacios
        flash('Mensaje Posteado', 'success')
        return redirect(url_for('index'))

    return render_template('post.html', form=form)


@app.route('/')
def index():
    """Vista principal. Muestra un timeline con los post de diferentes users"""

    stream = models.Post.select().limit(100)  # stream es el timeline
    return render_template('stream.html', stream=stream)


if __name__ == "__main__":
    """Función principal del proyecto. LLama a los demás métodos"""
    
    models.initialize()
    models.User.create_user(
        username='Guille',
        email='guillecor91@gmail.com',
        password="1234"  # Tiene que ser una cadena
    )

    app.run(debug=DEBUG, host=HOST, port=PORT)

# -----------------------------------------------------------------------------
# Lección 38 - Funcionalidad del logueo de los usuarios

# Para esta tarea, se usa el módulo de flask LoginManager()
