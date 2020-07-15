# g es un objeto global donde guardar la info de la app que queramos
# Como es global, es accesible en todo el proyecto.
# Para la ocasión, se usará para los métodos before y after request
# flash desplegar un mensaje después de la siguiente petición
# url_for es para generar una url a un cierto endpoint
from flask import Flask, g, render_template, flash, url_for, redirect
from flask_login import LoginManager
import models
import forms

DEBUG = True  # Mayúsuculas indica que es global (por convenio)
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)  # Se instancia la aplicación
app.secret_key = 'kaAsn4oeiASDL13JKHsdrjv<sklnv´lsjdAsCaxcAv'  # Llave Secreta.
# Se utiliza entre otras cosas para diferenciar esta app de otras en la web.
# Usar cualquier cadena, cuyos caracteres sean variados y aleatorios

login_manager = LoginManager()  # Se crea una variable donde alojarlo
login_manager.init_app(app)  # Login manager va a controlar las sesiones de app

# Qué vista mostrar cuando el usuario quiera loguearse o sea redirigido
login_manager.login_view('login')


@login_manager.user_loader
def load_user(userid):
    '''Método para cargar el usuario qué esté logueado'''

    try:
        # Devuelve el registro del usuario que tenga el mismo id que buscamos
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
            return None


# Por convenino se usan (y se nombrar así) los siguientes métodos:
# El nombre de los métodos es opcional.
# Lo que hace que tengan la característica especial deseada es el decorador
# Un decorador es una función que envuelven a otras funciones. Empiezan por @


@app.before_request  # Decorador
def before_request():
    '''Método que se ejecuta antes de hacer una petición (request) a la bbdd.
    - Establece las conexiones a la bbdd
    '''

    # Esta funcion verifica que el objeto g no tenga ya definido el atributo db
    # Esto evita errores al tratar de volver a definirlo.
    if not hasattr(g, 'db'):
        g.db = models.DB  # La bbdd es la definida en el archivo models
        g.db.connect()


@app.after_request
def after_request(response):  # response es la respuesta a la petición
    '''Método que se ejecuta después de hacer una petición (request) a la bbdd.
    - Cierra las conexiones con la bbdd
    '''

    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))  # Métodos HTTP usados aquí
def register():
    '''Vista para registrar un usuario'''
    form = forms.RegisterForm()
    if form.validate_on_submit():  # La información del formulario es válida
        flash('¡¡ Usted se ha registrado con éxito !!', success)
        models.User.create_user(  # Ahora podemos crear el usuario
            username = form.username.data,
            email = form.email.data,
            password = form.password.data
        )
        return redirect(url_for('index'))


@app.route('/')
def index():
    '''Vista principal'''

    return 'Hey'


    return g


if __name__ == "__main__":
    '''Función principal del proyecto. LLama a los demás métodos'''
    
    models.initialize()
    models.User.create_user(
        username='Guille',
        email='guillecor91@gmail.com',
        password=1234
    )

    app.run(debug=DEBUG, host=HOST, port=PORT)

# -----------------------------------------------------------------------------
# Lección 38 - Funcionalidad del logueo de los usuarios

# Para esta tarea, se usa el módulo de flask LoginManager()

