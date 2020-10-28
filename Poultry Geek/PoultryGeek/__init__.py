import os

# g es un objeto global donde guardar la info de la app que queramos
# Como es global, es accesible en todo el proyecto.
# Para la ocasión, se usará para los métodos before y after request
# flash -> desplegar un mensaje después de la siguiente petición
# url_for es para generar una url a un cierto endpoint
# abort te permite salir de la vista actual
from flask import (Flask, g, render_template, send_from_directory)

# Web de administración
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from flask_login import (LoginManager, current_user, AnonymousUserMixin)

# App
from PoultryGeek import forms  # LoginForm, RegisterForm
from PoultryGeek import models

DEBUG = True  # Mayúsculas indica que es global (por convenio)
PORT = 8000
HOST = '0.0.0.0'

UPLOAD_FOLDER = os.getcwd() + '/make_dataset/import_data'
MEDIA_FOLDER = os.getcwd() + '/media'

ALLOWED_EXTENSIONS = {'xlsx'}

CONFIGURACION = {
    'provincias'            : ['huelva', 'sevilla', 'badajoz', 'cordoba'],
    'tecnicos'              : ['carlos', 'sandra', 'eduardo'],
    'fabricas'              : ['nuter', 'picasat'],
    # 'nombre_integrado'    : ["AGROGANADERA MORANDOM", "JOSE MANUEL ROMERO MOLIN", "JUANA LOPEZ GUTIERREZ", "HNOS ALCAIDE, C.B.", "EDUARDO MARTÍN MARTÍN", "DEHESA LA ROTURA", "AGROGANADERA PINARES, SC", "HERMANOS CARRERO REYES, SC", "MIGUEL ANGEL GARRIDO TABODA", "DANIEL GALLARDO RODRIGUEZ", "AVES EL SAUCEJO, S.L.", "MANUEL PADILLA GARCÍA", "LUCAS REBOLLO ORTIZ", "JOSE ANTONIO BANDO MUÑOZ", "EXP.AGROPECUARIAS RIVERA DE HUELVA, S.L.", "CRISTOBAL MONCAYO HORMIGO", "DIEGO J. DOMINGUEZ ALBA", "JUAN LOPEZ GUTIERREZ", "ANTONIO CARDENAS BERLANGA", "JOSE DOMINGO SUAREZ LAVADO", "FRANCISCO JOSE CAMACHO SALAS", "VICTORINO RUBIO BRAVO", "BLAS ROMAN POVEA (INTEGRACION)", "BLAS ROMAN POVEA", "ALONSO ROBLES MORENO", "LOPEZ SOLTERO, SCA", "AGRICOLA HEREDIA MORENO, SC", "JUAN MANUEL CORONA RUEDA", "MJC. NARANJO RODIGUEZ,  SL", "LUIS ALFONSO VAZQUEZ", "MARIA DOLORES DOMINGUEZ GONZALEZ", "ROSARIO MINERO ", "CRISTAL RONCERO GONZÁLEZ", "AVEPRA, SL ", "AGROAVI PÉREZ VIDES", "MANUEL POVEA CARRASCO", "ENCARNACIÓN CLAVERO", "JUAN FERIA (FINCA VILLARAMOS)", "MARIA ISABEL MACIAS GARCIA", "MIGUEL ROSA BLANCO", "CONCEPCION MORATA ESTEPA", "CARMEN REAL ESTEBAN", "AVICOLA VALDELIMONES, S.L.", "FELIPE CALVENTE ROMERO", "MARIA VAZQUEZ RAMOS", "TEODORA DOMÍNGUEZ", "GONAN AVICULTURA, C.B.", "ISABEL CONTRERAS DOMINGUEZ", "JUAN SOSA CARMONA", "MANUEL CRUZ GARRIDO", "RICARDO SÁNCHEZ", "GONZALEZ MEJIAS E HIJOS, S.L.", "GENMA ORTIZ VAZQUEZ", "DEHESA SAN JUAN, SA", "RAUL ORTEGA JUAN", "MARIA JOSE RUIZ MOLINA", "GONAN AVICULTURA", "HNOS MATEOS, SCA", "ANTONIO VEGA PÉREZ", "BERNARDINO ROMERO, SL ", "LA PARRILLA 2000, SL"],
    'variables'             : ['integrado', 'pollos_entrados', 'pollos_salidos', 'porcentaje_bajas', 'kilos_carne', 'kilos_pienso', 'peso_medio', 'indice_transformacion', 'retribucion', 'medicamentos_por_pollo', 'dias_media_retirada', 'ganancia_media_diaria'],
    'poblaciones'           : ["la nava", "cartaya", "los corrales", "aracena", "santa ana la real", "escacema del campo", "fuentes de león", "villanueva de san juan", "nerva", "martin de la jara", "la palma del condado", "aljaraque", "san juan del puerto", "almonte", "bollullos del condado", "fuente de leon", "el saucejo", "barbara de casas", "pedrera", "tocina", "san silvestre de guzman", "almonaster la real", "trigueros", "valverde del camino", "jerez de los caballeros", "santa eufemia", "campofrio", "carboneras", "lepe", "segura de leon", "bellavista", "la puebla de los infantes", "moguer", "el patras", "monesterio", "castillo de las guardas", "villamanrique de la condesa", "pilas", "valdezufre"],
    'variables_evolucion'   : ["indice_transformacion", "peso_medio", "porcentaje_bajas", "retribucion", "ganancia_media_diaria"]
}

# Se instancia la aplicación
app = Flask(__name__, instance_relative_config=True)

app.secret_key = 'kaAsn4oeiASDL13JKHsdrjv<sklnv´lsjdAsCaxcAv'  # Llave Secreta.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MEDIA_FOLDER'] = MEDIA_FOLDER

from PoultryGeek.views import auth, evolution, load_data, table

# Blueprint
# Los blueprints se usan para poder hacer las rutas desde otros archivos
app.register_blueprint(auth.bp)
app.register_blueprint(load_data.bp)
app.register_blueprint(table.bp)
app.register_blueprint(evolution.bp)


# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# make url_for('index') == url_for('views.index')
app.add_url_rule("/", endpoint="index")
app.add_url_rule("/register", endpoint="register")
app.add_url_rule("/login", endpoint="login")
app.add_url_rule("/logout", endpoint="logout")
app.add_url_rule("/load_data", endpoint="load_data")
app.add_url_rule("/table", endpoint="table")
app.add_url_rule("/evolution", endpoint="evolution")


# Administración
app.config['FLASK_ADMIN_SWATCH'] = 'slate'  # Tema para la administracion
admin = Admin(app, name='Poultry Geek', template_mode='bootstrap3')

def admin_loader():
    # admin.add_view(ModelView(models.User)) # Reservado para superuser
    admin.add_view(ModelView(models.Integrado))
    admin.add_view(ModelView(models.Camada))
    admin.add_view(ModelView(models.Tecnico))
    admin.add_view(ModelView(models.Provincia))
    admin.add_view(ModelView(models.Fabrica))
    admin.add_view(ModelView(models.Poblacion))


# Usuario Invitado
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Invitado'

login_manager = LoginManager()  # Se crea una variable donde alojarlo
login_manager.init_app(app)  # Login manager va a controlar las sesiones de app
# Qué vista mostrar cuando el usuario quiera loguearse o sea redirigido
login_manager.login_view = 'login'
login_manager.anonymous_user = Anonymous  # El usuario es la propia clase


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


@login_manager.user_loader
def load_user(userid):
    """Método para cargar el usuario qué esté logueado"""

    try:
        # Devuelve el registro del usuario que tenga el mismo name que buscamos
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


# Se le pone una ruta distinta cada vez para que no cargue la img como estática
@app.route('/media/<path:filename>?')
def download_file(filename):
    return send_from_directory(app.config['MEDIA_FOLDER'], filename, as_attachment=True)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    """Vista principal. Muestra un timeline con los post de diferentes users"""

    # s = models.Post.select().limit(100)  # stream es el timeline
    # return render_template('stream.html', stream=s)
    return render_template('index.html')


if __name__ == "__main__":
    """Función principal del proyecto. LLama a los demás métodos"""

    models.initialize()


    # Carga algunos datos para poder empezar con la aplicación
    try:
        models.User.create_user(
            username='Guille',
            email='guillecor91@gmail.com',
            password="1234"  # Tiene que ser una cadena
        )
    except ValueError:  # Si el usuario ya está en la bbdd
        pass

    # Inicializar provincias
    for provincia in CONFIGURACION['provincias']:
        try:
            models.Provincia.create_provincia(
                nombre_provincia=provincia
            )
        except ValueError:  # Si la provincia ya está en la bbdd
            pass

    # Inicializar provincias
    for tecnico in CONFIGURACION['tecnicos']:
        try:
            models.Tecnico.create_tecnico(
                nombre_tecnico=tecnico
            )
        except ValueError:  # Si el tecnico ya está en la bbdd
            pass

    # Inicializar fabrica
    for fabrica in CONFIGURACION['fabricas']:
        try:
            models.Fabrica.create_fabrica(
                nombre_fabrica=fabrica
            )
        except ValueError:  # Si el fabrica ya está en la bbdd
            pass

    # Inicializar fabrica
    for poblacion in CONFIGURACION['poblaciones']:
        try:
            models.Poblacion.create_poblacion(
                nombre_poblacion=poblacion.strip().lower()
            )
        except ValueError:  # Si el fabrica ya está en la bbdd
            pass

    admin_loader()
    app.run(debug=DEBUG, host=HOST, port=PORT)


# ==============================================================================
# TODO

