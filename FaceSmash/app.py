# g es un objeto global donde guardar la info de la app que queramos
# Como es global, es accesible en todo el proyecto.
# Para la ocasión, se usará para los métodos before y after request
# flash -> desplegar un mensaje después de la siguiente petición
# url_for es para generar una url a un cierto endpoint
# abort te permite salir de la vista actual
from flask import (Flask, g, render_template, flash, url_for, redirect, abort,
                   request)
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
import sqlite3


import models

import forms  # LoginForm, RegisterForm

DEBUG = True  # Mayúsculas indica que es global (por convenio)
PORT = 8000
HOST = '0.0.0.0'
UPLOAD_FOLDER = os.getcwd() + '/make_dataset/import_data'
ALLOWED_EXTENSIONS = {'xlsx'}
CONFIGURACION = {
    'provincias'        : ['huelva', 'sevilla', 'badajoz', 'cordoba'],
    'tecnicos'          : ['carlos', 'sandra', 'eduardo'],
    # 'nombre_integrado'  : ["AGROGANADERA MORANDOM", "JOSE MANUEL ROMERO MOLIN", "JUANA LOPEZ GUTIERREZ", "HNOS ALCAIDE, C.B.", "EDUARDO MARTÍN MARTÍN", "DEHESA LA ROTURA", "AGROGANADERA PINARES, SC", "HERMANOS CARRERO REYES, SC", "MIGUEL ANGEL GARRIDO TABODA", "DANIEL GALLARDO RODRIGUEZ", "AVES EL SAUCEJO, S.L.", "MANUEL PADILLA GARCÍA", "LUCAS REBOLLO ORTIZ", "JOSE ANTONIO BANDO MUÑOZ", "EXP.AGROPECUARIAS RIVERA DE HUELVA, S.L.", "CRISTOBAL MONCAYO HORMIGO", "DIEGO J. DOMINGUEZ ALBA", "JUAN LOPEZ GUTIERREZ", "ANTONIO CARDENAS BERLANGA", "JOSE DOMINGO SUAREZ LAVADO", "FRANCISCO JOSE CAMACHO SALAS", "VICTORINO RUBIO BRAVO", "BLAS ROMAN POVEA (INTEGRACION)", "BLAS ROMAN POVEA", "ALONSO ROBLES MORENO", "LOPEZ SOLTERO, SCA", "AGRICOLA HEREDIA MORENO, SC", "JUAN MANUEL CORONA RUEDA", "MJC. NARANJO RODIGUEZ,  SL", "LUIS ALFONSO VAZQUEZ", "MARIA DOLORES DOMINGUEZ GONZALEZ", "ROSARIO MINERO ", "CRISTAL RONCERO GONZÁLEZ", "AVEPRA, SL ", "AGROAVI PÉREZ VIDES", "MANUEL POVEA CARRASCO", "ENCARNACIÓN CLAVERO", "JUAN FERIA (FINCA VILLARAMOS)", "MARIA ISABEL MACIAS GARCIA", "MIGUEL ROSA BLANCO", "CONCEPCION MORATA ESTEPA", "CARMEN REAL ESTEBAN", "AVICOLA VALDELIMONES, S.L.", "FELIPE CALVENTE ROMERO", "MARIA VAZQUEZ RAMOS", "TEODORA DOMÍNGUEZ", "GONAN AVICULTURA, C.B.", "ISABEL CONTRERAS DOMINGUEZ", "JUAN SOSA CARMONA", "MANUEL CRUZ GARRIDO", "RICARDO SÁNCHEZ", "GONZALEZ MEJIAS E HIJOS, S.L.", "GENMA ORTIZ VAZQUEZ", "DEHESA SAN JUAN, SA", "RAUL ORTEGA JUAN", "MARIA JOSE RUIZ MOLINA", "GONAN AVICULTURA", "HNOS MATEOS, SCA", "ANTONIO VEGA PÉREZ", "BERNARDINO ROMERO, SL ", "LA PARRILLA 2000, SL"],
    'campos_mostrados'  : ['integrado', 'pollos_entrados', 'pollos_salidos', 'porcentaje_bajas', 'kilos_carne', 'kilos_pienso', 'peso_medio', 'indice_transformacion', 'retribucion', 'medicamentos_por_pollo', 'dias_media_retirada', 'ganancia_media_diaria']
}


app = Flask(__name__)  # Se instancia la aplicación
app.secret_key = 'kaAsn4oeiASDL13JKHsdrjv<sklnv´lsjdAsCaxcAv'  # Llave Secreta.

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Administración
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'  # Tema para la administracion
admin = Admin(app, name='Poultry Geek', template_mode='bootstrap3')

def admin_loader():
    admin.add_view(ModelView(models.User))
    admin.add_view(ModelView(models.Integrado))
    admin.add_view(ModelView(models.Camada))
    admin.add_view(ModelView(models.Tecnico))
    admin.add_view(ModelView(models.Provincia))



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
                return redirect(url_for('index'))
            else:
                flash('Tu nombre de usuario o contraseña no existe', 'danger')

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


def check_provincia(nombre_provincia):

    if nombre_provincia.strip().lower() in CONFIGURACION['provincias']:
        return True
    else:
        return False


def check_tecnico(nombre_tecnico):

    if nombre_tecnico.strip().lower() in CONFIGURACION['tecnicos']:
        return True
    else:
        return False


def allowed_file(filename):
    """Comprueba si la extension del archivo es válida"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def dataset_to_bd(dataframe):
    """Procesa la información de un dataset y trata de guardarla en la bbdd"""

    d = dataframe.to_dict('index')

    registro_valido = True

    for registro in d:

        # Se validan los datos. Si falla salta el registro:
        registro_valido = registro_valido * check_provincia(d[registro]['Provincia'])
        registro_valido = registro_valido * check_tecnico(d[registro]['Técnico'])
        if(registro_valido):

            # Cojo la provincia que ya está en bbdd
            provincia = models.Provincia.get(
                models.Provincia.nombre_provincia **
                (d[registro]['Provincia']).strip().lower())

            tecnico = models.Tecnico.get(
                models.Tecnico.nombre_tecnico **
                (d[registro]['Técnico']).strip().lower())

            # Se crea el integrado
            models.Integrado.create_integrado(
                user=g.user._get_current_object(),
                tecnico=tecnico,
                fabrica=d[registro]['Fab. Pienso'],
                codigo=d[registro]['Código'],
                nombre_integrado=d[registro]['Avicultor'].strip().lower(),
                poblacion=d[registro]['Población'],
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
                        return redirect(url_for('index'))  # Si todo...
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
    """Devuelve un dataframe con la consulta realizada
        1) Se establece configuración
    """

    query = models.Camada.select().where(
        query_params["desde"] > models.Camada.fecha < query_params["hasta"]
    )

    df_query = pd.DataFrame(list(query.dicts()))

    # cnx = sqlite3.connect('social.db')
    # df_query = pd.read_sql_query("SELECT * FROM camada", cnx)
    # df_query = pd.read_sql_query(
    #     "SELECT * FROM camada WHERE fecha > '" + desde + "' AND  fehca <= '" + hasta + "'",
    #     cnx)

    return df_query

@login_required
@app.route('/search', methods=('GET', 'POST'))
def search():

    # Default query_params
    query_params = {
        "desde": "2015-01-01",
        "hasta": "2015-01-30",
        "num": 1
    }

    elementos_cabecera = []
    elementos_fila = []
    user = current_user

    query_params["num"] = request.form["num"]
    query_params["desde"] = request.form["desde"]
    query_params["hasta"] = request.form["hasta"]

    table = search_function(query_params)

    condicion = True

    if(condicion):
        del table['medicamentos']

<<<<<<< HEAD
    # print(table)
=======
    print(table)
>>>>>>> 4dfb9407a0ac2648d1d6f045ca918b1beac6cc1f

    for llave in table:
        if(llave in CONFIGURACION['campos_mostrados']):
            elementos_cabecera.append(llave.replace("_", " "))

    print(elementos_cabecera)

    # print(elementos_cabecera)

    print(elementos_cabecera)

    for i in table.index:
        lista_auxiliar = []
        for campo in CONFIGURACION['campos_mostrados']:
            if campo == 'porcentaje_bajas':
                valor = "{} %".format(round((table[campo][i] * 100), 2))
            elif campo == 'integrado':
                valor = table[campo][i]
            elif campo in ['pollos_entrados', 'pollos_salidos', 'kilos_carne', 'kilos_pienso']:
                valor = format((f'{table[campo][i]:,.0f}')).replace(',','~').replace('.',',').replace('~','.')
            else:
                valor = format((f'{table[campo][i]:,.4f}')).replace(',','~').replace('.',',').replace('~','.')

            lista_auxiliar.append(valor)

        # Se añade la fila
        elementos_fila.append(lista_auxiliar)



    # print(request.form["num"])

    return render_template('table.html',
                           elementos_cabecera=elementos_cabecera,
                           elementos_fila=elementos_fila,
                           query_params=query_params,
                           user=user,
                           form=request.form
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

    query_params = {
        "desde": "2015-01-01",
        "hasta": "2015-01-30",
        "num": 1
    }

    form = forms.SearchForm()

    # Se ejecuta el método si la validación al hacer click en el HTML es válida
    if form.validate_on_submit():
        if request.method == 'POST':
            print("Aqui llega 1")
            # query_params["desde"] = form.desde.data
            # query_params["hasta"] = form.hasta.data

            return redirect(url_for('table.html')
                            )
    else:
        return render_template('table.html',
                               form=form,
                               query_params=query_params
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
        except ValueError:  # Si el usuario ya está en la bbdd
            pass

        # Inicializar provincias
    for tecnico in CONFIGURACION['tecnicos']:
        try:
            models.Tecnico.create_tecnico(
                nombre_tecnico=tecnico
            )
        except ValueError:  # Si el usuario ya está en la bbdd
            pass

    admin_loader()
    app.run(debug=DEBUG, host=HOST, port=PORT)

# -----------------------------------------------------------------------------
# Lección 38 - Funcionalidad del logueo de los usuarios

# Para esta tarea, se usa el módulo de flask LoginManager()
