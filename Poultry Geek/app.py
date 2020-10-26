

# g es un objeto global donde guardar la info de la app que queramos
# Como es global, es accesible en todo el proyecto.
# Para la ocasión, se usará para los métodos before y after request
# flash -> desplegar un mensaje después de la siguiente petición
# url_for es para generar una url a un cierto endpoint
# abort te permite salir de la vista actual
from flask import (Flask, g, render_template, flash, url_for, redirect, abort,
                   request, send_from_directory)
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user, AnonymousUserMixin)
from flask_bcrypt import check_password_hash

# Importar archivos
from werkzeug.utils import secure_filename
import os
from make_dataset import process_data

# Web de administración
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView

# Tablas
import pandas as pd

# Gráficos
import time
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import math

# Predicción
from sklearn import linear_model

# App
import models
import forms  # LoginForm, RegisterForm
import utilidad

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


app = Flask(__name__)  # Se instancia la aplicación
app.secret_key = 'kaAsn4oeiASDL13JKHsdrjv<sklnv´lsjdAsCaxcAv'  # Llave Secreta.

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MEDIA_FOLDER'] = MEDIA_FOLDER

# Administración
app.config['FLASK_ADMIN_SWATCH'] = 'slate'  # Tema para la administracion
admin = Admin(app, name='Poultry Geek', template_mode='bootstrap3')

def admin_loader():
    # admin.add_view(ModelView(models.User))
    admin.add_view(ModelView(models.Integrado))
    admin.add_view(ModelView(models.Camada))
    admin.add_view(ModelView(models.Tecnico))
    admin.add_view(ModelView(models.Provincia))
    admin.add_view(ModelView(models.Fabrica))
    admin.add_view(ModelView(models.Poblacion))


# Se utiliza entre otras cosas para diferenciar esta app de otras en la web.
# Usar cualquier cadena, cuyos caracteres sean variados y aleatorios

# Usuario Invitado
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Invitado'

login_manager = LoginManager()  # Se crea una variable donde alojarlo
login_manager.init_app(app)  # Login manager va a controlar las sesiones de app

# Qué vista mostrar cuando el usuario quiera loguearse o sea redirigido
login_manager.login_view = 'login'
login_manager.anonymous_user = Anonymous  # El usuario es la propia clase


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


# Se le pone una ruta distinta cada vez para que no cargue la img como estática
@app.route('/media/<path:filename>?')
def download_file(filename):
    return send_from_directory(app.config['MEDIA_FOLDER'], filename, as_attachment=True)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """Te permite consultar un post dado su id"""

    # El Post.id es automático. Se genera cuando se crea el registro
    s = models.Post.select().where(models.Post.id == post_id)
    if s.count() == 0:
        abort(404)
    return render_template('stream.html', stream=s)


@app.route('/follow/<username>')
@login_required
def follow(username):
    """Crea una nueva relación (Nueva entrada en la tabla Relationship)"""

    try:
        # Coges al usuario que quieres seguir
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:  # En caso de que no lo encuentre
        abort(404)
    else:  # Si se encuentra el usuario que queremos seguir en la bd...
        try:  # Se crea la relación
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:  # La relación ya se ha creado antes
            abort(404)
        else:
            flash('Ahora sigues a {}'.format(to_user.username), 'success')
    # Redirige al stream (los post) del usuario que hemos seguido
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """Borra una relación existente"""

    try:
        # Coges al usuario que quieres dejar de seguir
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:  # En caso de que no lo encuentre
        abort(404)
    else:  # Si se encuentra el usuario que queremos seguir en la bd...
        try:  # Se crea la relación
            models.Relationship.get(  # Coges el registro de esta persona
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:  # La relación ya se ha creado antes
            abort(404)
        else:
            flash('Has dejado de seguir a {}'.format(to_user.username),
                  'success')
    # Redirige al stream (los post) del usuario que hemos seguido
    return redirect(url_for('stream', username=to_user.username))


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
            flash('Tu nombre de usuario o contraseña no existe', 'danger')
        else:  # Si el usuario si existe hay que comprobar su contraseña
            if check_password_hash(user.password, form.password.data):
                login_user(user)  # Se loguea con la librería de flask
                flash('Has iniciado sesión', 'success')
                return redirect(url_for('evolution'))
            else:
                flash('Tu nombre de usuario o contraseña no existe', 'danger')

    return render_template('login.html', form=form)  # Usa macro para render


@app.route('/logout')
@login_required  # Puede haber más de un decorador. Este requiere estar logado
def logout():
    """Permite cerrar sesión al usuario"""

    logout_user()  # Termina la sesión de usuario
    flash('Has salido de Poultry Geek', 'success')
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


def check_provincia(nombre_provincia):

    if nombre_provincia.strip().lower() in CONFIGURACION['provincias']:
        return True
    else:
        print("nombre provincia no valido")
        return False


def check_tecnico(nombre_tecnico):

    if nombre_tecnico.strip().lower() in CONFIGURACION['tecnicos']:
        return True
    else:
        print("tecnico no valido")
        return False


def check_fabrica(nombre_fabrica):

    if nombre_fabrica.strip().lower() in CONFIGURACION['fabricas']:
        return True
    else:
        print("fabrica no valido")
        return False

def check_poblacion(nombre_poblacion):

    if nombre_poblacion.strip().lower() in CONFIGURACION['poblaciones']:
        return True
    else:
        print("poblacion no valido")
        return False


def allowed_file(filename):
    """Comprueba si la extension del archivo es válida"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def dataset_to_bd(dataframe):
    """Procesa la información de un dataset y trata de guardarla en la bbdd"""

    d = dataframe.to_dict('index')

    for registro in d:


        registro_valido = True

        # Se validan los datos. Si falla salta el registro:
        registro_valido = registro_valido\
                          * check_provincia(d[registro]['Provincia'])\
                          * check_tecnico(d[registro]['Técnico'])\
                          * check_fabrica(d[registro]['Fab. Pienso'])\
                          * check_poblacion(d[registro]['Población'])

        if(registro_valido):

            # Cojo la provincia que ya está en bbdd
            provincia = models.Provincia.get(
                models.Provincia.nombre_provincia **
                (d[registro]['Provincia']).strip().lower())

            tecnico = models.Tecnico.get(
                models.Tecnico.nombre_tecnico **
                (d[registro]['Técnico']).strip().lower())

            fabrica = models.Fabrica.get(
                models.Fabrica.nombre_fabrica **
                (d[registro]['Fab. Pienso']).strip().lower())

            poblacion = models.Poblacion.get(
                models.Poblacion.nombre_poblacion **
                (d[registro]['Población']).strip().lower())

            # Se crea el integrado
            models.Integrado.create_integrado(
                user=g.user._get_current_object(),
                tecnico=tecnico,
                fabrica=fabrica,
                codigo=d[registro]['Código'],
                nombre_integrado=d[registro]['Avicultor'].strip().lower(),
                poblacion=poblacion,
                provincia=provincia,
                ditancia=d[registro]['Distancia a Matadero Purullena'],
                metros_cuadrados=d[registro]['Mts Cuadrados'],
            )

            # ==================================================================

            # Cojo el integrado que ya está en bbdd
            integrado = models.Integrado.get(
                models.Integrado.nombre_integrado**
                d[registro]['Avicultor'].strip().lower())

            # print(integrado)

            # print("El tipo de dato de fecha es: ", type(d[registro]['FECHA']))

            # Se crea la camada
            models.Camada.create_camada(
                integrado=integrado,
                codigo_camada=d[registro]['Código Camada'],
                medicamentos=d[registro]['MEDICAMENTOS'],
                liquidacion=d[registro]['LIQUIDACIÓN'],
                pollos_entrados=d[registro]['Pollos Entrados'],
                pollos_salidos=d[registro]['Pollos Salidos'],
                porcentaje_bajas=d[registro]['% Bajas'],
                bajas_primera_semana=d[registro]['BAJAS 1a. SEMANA'],
                porcentaje_bajas_primera_semana=d[registro]['%BAJAS 1a. Semana'],
                kilos_carne=d[registro]['Kilos Carne'],
                kilos_pienso=d[registro]['Kilos Pienso'],
                peso_medio=d[registro]['Peso Medio'],
                indice_transformacion=d[registro]['I.Transform'],
                retribucion=d[registro]['Retribución Pollo'],
                medicamentos_por_pollo=d[registro]['Medic/Pollo'],
                rendimiento_metro_cuadrado=d[registro]['Rdto/M2'],
                pollo_metro_cuadrado=d[registro]['Pollo/Mt2'],
                kilos_consumidos_por_pollo_salido=d[registro]['Kilos Consumidos por Pollo Salido'],
                dias_media_retirada=d[registro]['Dias Media Retirada sin Asador'],
                ganancia_media_diaria=d[registro]['Ganancia Media Diaria'],
                dias_primer_camion=d[registro]['Días Primer Camión'],
                peso_primer_dia=d[registro]['Peso 1 Día'],
                peso_semana_1=d[registro]['Peso 1 Semana'],
                peso_semana_2=d[registro]['peso 2 semana'],
                peso_semana_3=d[registro]['peso 3 semana'],
                peso_semana_4=d[registro]['peso 4 semana'],
                peso_semana_5=d[registro]['peso 5 semana'],
                peso_semana_6=d[registro]['peso 6 semana'],
                peso_semana_7=d[registro]['peso 7 semana'],
                fecha=d[registro]['FECHA'],
                rendimiento=d[registro]['Rendimiento'],
                FP=d[registro]['%  FP'],
                bajas_matadero=d[registro]['Bajas'],
                decomisos_matadero=d[registro]['Decomisos'],
                porcentaje_bajas_matadero=d[registro]['% Bajas'],
                porcentaje_decomisos=d[registro]['% Decomisos'],
            )

    return True


@app.route('/load_data', methods=('GET', 'POST'))
@login_required  # Puede haber más de un decorador. Este requiere estar logado
def load_data():
    """Permite cargar datos a la bbdd usando el formulario correspondiente"""


    form = forms.LoadDataForm()

    if form.validate_on_submit():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part', 'danger')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file', "danger")
                return redirect(request.url)
            if file:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                           filename))
                    # Una vez cargados en el servidor, hay que procesarlos
                    dataframe = process_data(
                        os.path.join(app.config['UPLOAD_FOLDER'],
                        filename))
                    # Ahora se carga en la bd
                    if dataset_to_bd(dataframe):
                        flash("Datos cargados con éxito", "success")
                        return render_template('evolution.html',
                                               variables_evolucion=CONFIGURACION["variables_evolucion"],
                                               url_variable=time.strftime(
                                                   "%Y%m%d%H%M%S")
                                               )

                        return redirect(url_for('evolution'))  # Si todo...
                    else:
                        flash('No se pudieron procesar los datos', "danger")
                    # va bien vuelve al index
                else:
                    flash('Extensión de fichero no válida', 'danger')

    return render_template('load_data.html', form=form)  # Vuelve a intentarlo



@app.route('/')
def index():
    """Vista principal. Muestra un timeline con los post de diferentes users"""

    # s = models.Post.select().limit(100)  # stream es el timeline
    # return render_template('stream.html', stream=s)
    return render_template('index.html')


@app.route('/stream')  # timeline del usuario que ha iniciado sesión
@app.route('/stream/<username>')  # timeline de un usuario específico
def stream(username=None):
    """
    Muestra hasta 100 post
    - Cuando no se le proporciona nombre de usuario, te muestra el general
    - Cuando se le proporciona un nombre te muestra solo los de ese usuario
    """

    template = 'stream.html'  # Para el usuario que ha iniciado sesión
    if username and username != current_user.username:
        # Si es otro usuario diferente que le que ha iniciado sesión
        try:

            # El ** sirve para hacer like. Ignora mayúsculas y minúsculas
            # .get() solo te da un registro, una instancia
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)  # Despliega el código de error (404) al usuario
        else:  # Si no ocurre la excepción
            s = user.posts.limit(100)
    else:
        # Si el usuario es el mismo que ha iniciado sesión
        s = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'  # Para otro usuario
    return render_template(template, stream=s, user=user)

# def get_query_params(query_params):
#     """Permite realizar una nueva búsqueda con el formulario de búsqueda"""
#
#     form = forms.SearchForm()
#
#     # Se ejecuta el método si la validación al hacer click en el HTML es válida
#     if form.validate_on_submit():
#         query_params["desde"]=form.desde.data
#         query_params["hasta"]=form.hasta.data
#
#         return render_template('table.html', form=form)
#
#     return query_params

def search_function(query_params):
    """Devuelve un dataframe con la consulta realizada"""

    print("desde: ", query_params["desde"])
    print("hasta: ", query_params["hasta"])

    if query_params["avicultor"] == "Todos":
        query = models.Camada.select().where(
                (models.Camada.fecha >= query_params["desde"]) &
                (models.Camada.fecha < query_params["hasta"])
        )
    else:
        query = (models.Camada
            .select(models.Camada, models.Integrado)
            .join(models.Integrado)
            .group_by(models.Camada.codigo_camada)
            .where(
                (models.Camada.fecha >= query_params["desde"]) &
                (models.Camada.fecha < query_params["hasta"]) &
                (models.Camada.integrado.nombre_integrado == query_params["avicultor"]) &
                (models.Camada.integrado == models.Integrado.nombre_integrado)
            )
        )

    df_query = pd.DataFrame(list(query.dicts()))

    # cnx = sqlite3.connect('social.db')
    # df_query = pd.read_sql_query("SELECT * FROM camada", cnx)
    # df_query = pd.read_sql_query(
    #     "SELECT * FROM camada WHERE fecha > '" + desde + "' AND  fehca <= '" + hasta + "'",
    #     cnx)

    return df_query


def numero_dias_intervalo(desde, hasta):

    print("Desde: ", desde)
    print("Hasta: ", hasta)

    d1 = datetime.strptime(desde, "%Y-%m-%d")
    d2 = datetime.strptime(hasta, "%Y-%m-%d")

    return abs((d2 - d1).days)

def calcular_medias_intervalo(datos, desde, hasta, variable):

    # a = pd.DataFrame([
    #     "2015-01-01",
    #     "2015-01-21",
    #     "2015-03-01",
    #     "2015-04-05",
    #     "2015-06-12",
    #     "2015-05-23",
    #     "2015-06-13",
    #     "2015-04-13",
    #     "2015-02-13",
    # ]) #

    # el nº de intervalos se determina en funcion del nº de dias del periodo
    numero_dias = numero_dias_intervalo(desde, hasta)

    if (numero_dias >= 360) & (numero_dias < 370): # Se trata de un año
        num_periodos = 5 # se divide en trimestres
    elif (numero_dias < 11): # No hará nada si el periodo es demasiado pequeño
        return None
    else: # para cualquier otro periodo de tiempo se divide en 10
        num_periodos = 11


    # if num_dias > 30, elif > 90 ...

    periodos = pd.date_range(
        start=desde,
        end=hasta,
        periods=num_periodos # 1 más de lo que queremos en realidad
    )

    print(periodos)

    # time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
     # b= datos[b[0] <= datos['fecha'] < b[1]]

    # Primero convierto la hora en datatime para poder comparar
    datos['fecha'] = pd.to_datetime(datos['fecha'], format="%Y-%m-%d")

    # print("periodo0: ", periodos[0])
    # print("periodo1: ", periodos[1])

    medias = []
    ultimo_valido = 0

    # Calculo las medias teniendo en cuanta los periodos
    for i in (range(len(periodos) - 1)):
        media = (
                datos[variable][ # Solo de la variable en cuestion
                    (datos['fecha'] >= periodos[i]) &
                    (datos['fecha'] < periodos[i+1])
                ]
        ).mean()

        if math.isnan(media): # Si el valor es nan
            medias.append(ultimo_valido)
        else:
            medias.append(media)
            ultimo_valido = media


    print(medias)



    # medias = a.rolling(
    #     window=3
    # ).mean()

    # medias = pd.rolling_mean(
    #     arg = table["pollos_entrados"],
    #     window=3
    # )
    return medias

def grafico_evolucion_variables(medias, nombre_variable):
    # Data for plotting
    x = np.arange(0, len(medias), 1)
    y = medias

    width = 0.5
    plt.clf()
    barras = plt.bar(x, y, width, color='green')

    # Se determina el eje de la y en función de los valores mínimos y máximos
    plt.ylim(min(medias) - (min(medias) * 0.1),
             max(medias) + (max(medias) * 0.1))

    # p1 = plt.bar(ind, menMeans, width, yerr=menStd)

    # barras.set(
    #     xlabel='time (s)',
    #     ylabel='voltage (mV)',
    #     title='About as simple as it gets, folks'
    # )

    plt.title(nombre_variable)

    meses = (
        'ene',
        'feb',
        'mar',
        'abr',
        'may',
        'jun',
        'jul',
        'ago',
        'sep',
        'oct',
        'nov',
        'dic'
    )

    trimestres =(
        '1er. trimestre',
        "2º trimestre",
        "3º trimestre",
        "4º trimestre"
    )

    # N = 5
    # menMeans = (20, 35, 30, 35, 27)
    # womenMeans = (25, 32, 34, 20, 25)
    # menStd = (2, 3, 4, 1, 2)
    # womenStd = (3, 5, 2, 3, 3)
    # ind = np.arange(N)  # the x locations for the groups
    # width = 0.35  # the width of the bars: can also be len(x) sequence
    #
    # p1 = plt.bar(ind, menMeans, width, yerr=menStd)
    # p2 = plt.bar(ind, womenMeans, width,
    #              bottom=menMeans, yerr=womenStd)
    #
    # plt.ylabel('Scores')
    # plt.title('Scores by group and gender')
    # plt.xticks(ind, ('G1', 'G2', 'G3', 'G4', 'G5'))
    # plt.yticks(np.arange(0, 81, 10))
    # plt.legend((p1[0], p2[0]), ('Men', 'Women'))
    #
    # plt.show()

    # El nombre de los meses son las etiquetas del eje x

    if(len(medias) == 4):
        plt.xticks(ticks=x, labels=trimestres, rotation=-45)
    else:
        plt.xticks(ticks=x)

    plt.grid(barras, axis="y", alpha=0.1)

    ruta_archivo_imagen = os.getcwd() + '/media/media_' + nombre_variable + '.svg'


    plt.savefig(ruta_archivo_imagen, orientation="landscape", bbox_inches="tight", pad_inches=0.2)
    # plt.show()

    pass


def predecir(variables_a_predecir):
    """ Predice la media del mes siguiente para un conjunto de variables """

    # Esto es lo que hay que pasarle


    medias = utilidad.calcular_medias_por_mes(variables_a_predecir)


    # print(medias[2015]['indice_transformacion'])


    # for anno in medias:
    #     for variable in medias[anno]:
    #         # print(medias[anno][variable])
    #         for mes in medias[anno][variable]:
    #             print(mes)

    dict_variable_medias = {}

    # Inicializo las listas para añadirles elementos
    for variable in variables_a_predecir:
        dict_variable_medias[variable] = []

    # Se prepara el formato para el proceso
    for anno in medias:
        for variable in medias[anno]:
            # print(medias[anno][variable])
            for mes in medias[anno][variable]:
                dict_variable_medias[variable].append(mes)

    print(dict_variable_medias)

    # Lista de parámetros:
    intervalo = 0
    num_variables_lag = 3

    # m0 = [9, 8, 7, 7, 7, 5, 3, 5, 5, 6, 7, 4, 5, 7, 5, 4, 3, 5, 6, 7, 8, 5]
    # m1 = [9, 8, 7, 2, 7, 3, 7, 5, 8, 6, 4, 2, 2, 1, 9, 4, 3, 1, 3, 2, 8, 1]

    # # Esto es lo que hay que pasarle
    # dict_variable_medias = {
    #     'pollos_entrados': m0,
    #     'pollos_salidos': m1,
    # }

    lista_valores_y = []
    lista_valores_x = []

    for variable in dict_variable_medias.keys():
        print(variable)

        dataframe_medias = pd.DataFrame(dict_variable_medias[variable])

        # Se crea la primera columna de la tabla
        tabla_de_variable = pd.DataFrame(
            dict_variable_medias[variable],
            columns=[variable]
        )

        # Se forman las variables con lag y con ellas se completa la tabla
        for i in range(num_variables_lag):
            # indice = 'C' + str(i)
            dataframe_medias = dataframe_medias.shift(periods=1)
            tabla_de_variable.insert(i + 1, (variable + "_t-" + str(i + 1)),
                                     dataframe_medias)
        #
        # Se forma el conjunto de resultados (columna y)
        y = pd.DataFrame(
            dict_variable_medias[variable],
            columns=["y"]
        )
        y = y.shift(periods=-1)  # Se desplaza una posición hacia arriba

        # print("La tabla original\n", tabla, y)

        # Se quitan las filas con valores NaN (Se capa por arriba).
        conjunto_x = tabla_de_variable[num_variables_lag:]  # tanto en la tabla
        conjunto_y = y[num_variables_lag:]  # como en la columna de resultados

        # Se elimina el último resultado de 'y' (NaN)
        conjunto_y = conjunto_y.iloc[:-1]

        # Se añade este conjunto para posteriormente poder predecir la variable
        lista_valores_x.append(conjunto_x)
        lista_valores_y.append(conjunto_y)

    # Se concatenan las tablas de los valores x
    tabla_final = pd.concat(lista_valores_x, axis='columns')

    # print("La tabla final al principio\n\n", tabla_final)

    # Se saca la variable a predecir:
    patron_a_predecir = tabla_final.tail(1)  # Se trata del último patron
    # print("patron a predecir" + str(patron_a_predecir.shape) + ". \n", patron_a_predecir)

    # Una vez sacado el patron a predecir, se elimina de la tabla
    tabla_final = tabla_final.iloc[:-1]

    print("La tabla final:\n\n", tabla_final)

    # ==========================================================================

    # Usar todos los datos disponibles para predecir
    # Se aplica el modelo que se haya determinado
    # Se hace para cada una de las variables

    regr = linear_model.LinearRegression()
    medias_predichas = []

    for y_variable in lista_valores_y:
        regr.fit(tabla_final, y_variable)
        y_pred = regr.predict(patron_a_predecir)
        medias_predichas.append(y_pred[0][0])

    # print(medias_predichas)

    # Se añaden a las medias
    i = 0
    for variable in dict_variable_medias:
        dict_variable_medias[variable].append(medias_predichas[i])
        i = i + 1
        # print(dict_variable_medias[variable])
        utilidad.graficos_evolucion(dict_variable_medias[variable], variable)




@app.route('/evolution')
def evolution():
    """
    - Hay que hacer una consulta con todos los datos de toda la integracion
    - se forma el dataset
    - se cogen las medias de las 3 variables
    -


    """

    # Se envía una lista de las variables a predecir

    variables_a_predecir = [
        "indice_transformacion",
        "retribucion",
        "porcentaje_bajas",
        "ganancia_media_diaria",
        "peso_medio"
    ]

    # HACER LA TABLA
    predecir(variables_a_predecir)

    print("Fin Prediccion:")

    print(CONFIGURACION["variables_evolucion"])

    return render_template('evolution.html',
                           variables_evolucion=CONFIGURACION[
                               "variables_evolucion"],
                           url_variable=time.strftime(
                               "%Y%m%d%H%M%S")
                           )


@login_required
@app.route('/search', methods=('GET', 'POST'))
def search():

    # Default query_params
    query_params = {
        "desde": "2015-01-01",
        "hasta": "2015-01-30",
        "num": 1,
        "avicultor": "Todos",
        "variables": ['integrado', 'pollos_entrados', 'pollos_salidos',
                      'porcentaje_bajas', 'kilos_carne', 'kilos_pienso',
                      'peso_medio', 'indice_transformacion', 'retribucion',
                      'medicamentos_por_pollo', 'dias_media_retirada',
                      'ganancia_media_diaria'],
        "ch_variables" :   {
                'integrado' : "on",
                'pollos_entrados' : "on",
                'pollos_salidos' : "on",
                'porcentaje_bajas' : "on",
                'kilos_carne' : "on",
                'kilos_pienso' : "on",
                'peso_medio' : "on",
                'indice_transformacion' : "on",
                'retribucion' : "on",
                'medicamentos_por_pollo' : "on",
                'dias_media_retirada' : "on",
                'ganancia_media_diaria' : "on",
            }
    }

    elementos_cabecera = []
    elementos_fila = []
    user = current_user

    # query_params["num"] = request.form["num"]
    query_params["desde"] = request.form["desde"]
    query_params["hasta"] = request.form["hasta"]
    query_params["avicultor"] = request.form["avicultor"]

    # print("queryparams antes: ", query_params["ch_variables"]["pollos_entrados"])

    for variable in query_params["ch_variables"]:
        query_params["ch_variables"][variable] = request.form.get(
            "ch_" + variable)

    # print("queryparams despues: ",
    #       query_params["ch_variables"]["pollos_entrados"])

    # print("form: ", request.form.get("ch_pollos_entrados"))

    table = search_function(query_params)

    # Aquí selecciono las variables a mostrar según el formulario en una lista
    variables_mostradas = []

    for variable in CONFIGURACION['variables']:
        if request.form.get("ch_" + variable) == "on":
            variables_mostradas.append(variable)
        else:
            # print("desactivado: ", variable)
            if variable in variables_mostradas:
                variables_mostradas.remove(variable)

    for llave in table:
        if(llave in variables_mostradas):
            elementos_cabecera.append(llave.replace("_", " "))

    estadisticas = {}

    # Se rellena en el mismo orden que van a aparecer en la tabla
    for variable in variables_mostradas:
        if variable != "integrado": # no es una variable numérica
            lista_por_variable = []

            if variable == 'porcentaje_bajas':
                lista_por_variable.append(
                    "{} %".format(round((table[variable].mean() * 100), 2)).replace(',','~').replace('.',',').replace('~','.')
                )
                lista_por_variable.append(
                    "{} %".format(round((table[variable].std() * 100), 2)).replace(',','~').replace('.',',').replace('~','.')
                )
            else:
                lista_por_variable.append(
                    format((f'{table[variable].mean():,.4f}')).replace(',','~').replace('.', ',').replace('~', '.')
                )
                lista_por_variable.append(
                    format((f'{table[variable].std():,.4f}')).replace(',','~').replace('.', ',').replace('~', '.')
                )


            estadisticas[variable] = lista_por_variable

    print(estadisticas)

    # print(elementos_cabecera)

    # print(elementos_cabecera)

    for i in table.index:
        lista_auxiliar = []
        for campo in variables_mostradas:
            # Porcentaje
            if campo == 'porcentaje_bajas':
                valor = "{} %".format(round((table[campo][i] * 100), 2))
            # Cadena de texto
            elif campo == 'integrado':
                valor = table[campo][i]
            # separador de miles y sin decimales
            elif campo in ['pollos_entrados', 'pollos_salidos', 'kilos_carne', 'kilos_pienso']:
                valor = format((f'{table[campo][i]:,.0f}')).replace(',','~').replace('.',',').replace('~','.')
            # separador de miles y 4 decimales
            else:
                valor = format((f'{table[campo][i]:,.4f}')).replace(',','~').replace('.',',').replace('~','.')

            lista_auxiliar.append(valor)

        # Se añade la fila
        elementos_fila.append(lista_auxiliar)

    # Coger el nombre de los avicultores disponible
    avicultores = models.Integrado.select(models.Integrado.nombre_integrado).execute()

    # print(request.form["num"])
    # print("El numero de dias es: ", numero_dias_intervalo(query_params["desde"], query_params["hasta"]))


    # num_dias = numero_dias_intervalo(query_params["desde"],
    #                                  query_params["hasta"])


    # Se crean los gráficos
    for variable in variables_mostradas:
        if variable != "integrado":
            medias = calcular_medias_intervalo(
                datos=table,
                desde=query_params["desde"],
                hasta=query_params["hasta"],
                variable=variable
            )
            print("Las medias son: ", medias)
            grafico_evolucion_variables(medias, nombre_variable=variable)


    # Se le pone una ruta distinta cada vez para que no cargue la img como estática
    url_variable = time.strftime("%Y%m%d%H%M%S")

    return render_template('table.html',
                           elementos_cabecera=elementos_cabecera,
                           elementos_fila=elementos_fila,
                           query_params=query_params,
                           user=user,
                           avicultores=avicultores,
                           form=request.form,
                           estadisticas=estadisticas,
                           url_variable=url_variable
                           )

@login_required
@app.route('/table', methods=('GET', 'POST'))
def show_table():
    """
    Muestra hasta 100 post
    - Cuando no se le proporciona nombre de usuario, te muestra el general
    - Cuando se le proporciona un nombre te muestra solo los de ese usuario
    """

    # s = current_user.get_integrado().limit(100)

    # table = pd.DataFrame({'name': ['Somu', 'Kiku', 'Amol', 'Lini', 'Guille'],
    #                          'physics': [68, 74, 77, 78, 56],
    #                          'chemistry': [84, 56, 73, 69, 48],
    #                          'algebra': [78, 88, 82, 87, 98]})

    # Default query_params
    # Default query_params
    query_params = {
        "desde": "2015-01-01",
        "hasta": "2015-01-30",
        "num": 1,
        "avicultor": "Todos",
        "variables": ['integrado', 'pollos_entrados', 'pollos_salidos',
                      'porcentaje_bajas', 'kilos_carne', 'kilos_pienso',
                      'peso_medio', 'indice_transformacion', 'retribucion',
                      'medicamentos_por_pollo', 'dias_media_retirada',
                      'ganancia_media_diaria'],
        "ch_variables" :   {
                'integrado' : "on",
                'pollos_entrados' : "on",
                'pollos_salidos' : "on",
                'porcentaje_bajas' : "on",
                'kilos_carne' : "on",
                'kilos_pienso' : "on",
                'peso_medio' : "on",
                'indice_transformacion' : "on",
                'retribucion' : "on",
                'medicamentos_por_pollo' : "on",
                'dias_media_retirada' : "on",
                'ganancia_media_diaria' : "on",
            }
    }

    avicultores = models.Integrado.select(
        models.Integrado.nombre_integrado).execute()

    form = forms.SearchForm()

    # Se ejecuta el método si la validación al hacer click en el HTML es válida
    if form.validate_on_submit():
        if request.method == 'POST':
            # query_params["desde"] = form.desde.data
            # query_params["hasta"] = form.hasta.data

            return redirect(url_for('table.html')
                            )
    else:
        return render_template('table.html',
                               form=form,
                               query_params=query_params,
                               avicultores=avicultores
                               )


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

if __name__ == "__main__":
    """Función principal del proyecto. LLama a los demás métodos"""

    models.initialize()
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

# -----------------------------------------------------------------------------
# Lección 38 - Funcionalidad del logueo de los usuarios

# Para esta tarea, se usa el módulo de flask LoginManager()
