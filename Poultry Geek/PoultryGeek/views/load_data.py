from flask import Blueprint

import os
import time

from flask import (g, render_template, flash, url_for, redirect, request,
                   Markup)
from flask_login import (login_required)
from werkzeug.utils import secure_filename # Importar archivos

import pandas as pd

from datetime import date, datetime, time

# App
from PoultryGeek import CONFIGURACION
from PoultryGeek import app
from PoultryGeek import forms
from PoultryGeek import models



ALLOWED_EXTENSIONS = {'xlsx'}

bp = Blueprint("load_data", __name__, template_folder='templates', static_folder='static')


# ==============================================================================

RESULTADO_SUBIDA = {
    'nombre_provincia'  : set(),
    'nombre_tecnico'    : set(),
    'nombre_fabrica'    : set(),
    'nombre_poblacion'  : set(),
    'n_nombre_provincia'  : 0,
    'n_nombre_tecnico'    : 0,
    'n_nombre_fabrica'    : 0,
    'n_nombre_poblacion'  : 0,
    'n_total_registros_analizados' : 0,
    'n_camadas_subidas' : 0,
    'n_integrados_subidos' : 0,
}


def check_provincia(nombre_provincia):

    if nombre_provincia.strip().lower() in CONFIGURACION['provincias']:
        return True
    else:
        # print("nombre provincia no valido")

        RESULTADO_SUBIDA['nombre_provincia'].add(
            nombre_provincia.strip().lower()
        )

        RESULTADO_SUBIDA['n_nombre_provincia'] = (
            RESULTADO_SUBIDA['n_nombre_provincia'] + 1
        )

        # print("Check: n_nombre_provincia",
        #       RESULTADO_SUBIDA['n_nombre_provincia'])
        #
        # print("Check: nombre_provincia",
        #       RESULTADO_SUBIDA['nombre_provincia'])

        return False


def check_tecnico(nombre_tecnico):

    if nombre_tecnico.strip().lower() in CONFIGURACION['tecnicos']:
        return True
    else:
        # print("tecnico no valido")
        return False


def check_fabrica(nombre_fabrica):

    if nombre_fabrica.strip().lower() in CONFIGURACION['fabricas']:
        return True
    else:
        # print("fabrica no valido")
        RESULTADO_SUBIDA['nombre_fabrica'].add(
            nombre_fabrica.strip().lower()
        )

        RESULTADO_SUBIDA['n_nombre_fabrica'] = (
            RESULTADO_SUBIDA['n_nombre_fabrica'] + 1
        )

        # print("Check: n_nombre_fabrica",
        #       RESULTADO_SUBIDA['n_nombre_fabrica'])

        return False

def check_poblacion(nombre_poblacion):

    if nombre_poblacion.strip().lower() in CONFIGURACION['poblaciones']:
        return True
    else:
        # print("poblacion no valido")
        return False


def check_fecha(fecha):
    """
    Comprueba si el formato de la fecha es correcto
    y si está en un intervalo válido
    """
    print("el tipo de la fecha es: ", type(fecha))
    print("La fecha es: ", fecha)

    # Solo datos comprendidos entre 2015 y la fecha actual
    try:
        if (
                (fecha > datetime.strptime("2014-12-31", "%Y-%m-%d"))
                &
                (fecha <= datetime.today())
        ):
            return True
        else:
            return False
    except:
        return False

    return True


def dataset_to_bd(dataframe):
    """Procesa la información de un dataset y trata de guardarla en la bbdd"""

    d = dataframe.to_dict('index')

    for registro in d:

        RESULTADO_SUBIDA['n_total_registros_analizados'] = (
            RESULTADO_SUBIDA['n_total_registros_analizados'] + 1
        )

        registro_valido = True

        # Se validan los datos. Si falla salta el registro:
        registro_valido = (registro_valido
                          * check_provincia(d[registro]['Provincia'])
                          * check_tecnico(d[registro]['Técnico'])
                          * check_fabrica(d[registro]['Fab. Pienso'])
                          * check_poblacion(d[registro]['Población'])
                          * check_fecha(d[registro]['FECHA'])
                           )

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
            creado = models.Integrado.create_integrado(
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

            if creado:
                RESULTADO_SUBIDA['n_integrados_subidos'] = (
                        RESULTADO_SUBIDA['n_integrados_subidos'] + 1)

            # ==================================================================

            # Cojo el integrado que ya está en bbdd
            integrado = models.Integrado.get(
                models.Integrado.nombre_integrado **
                d[registro]['Avicultor'].strip().lower())

            # print(integrado)


                # try:
                #     d[registro]['FECHA'] = datetime.fromtimestamp(d[registro]['FECHA'])
                # except:
                #     pass


            print("El tipo es:   ", type(d[registro]['FECHA']))

            # print("El tipo de dato de fecha es: ", type(d[registro]['FECHA']))

            # Se crea la camada
            try:
                creado = models.Camada.create_camada(
                    integrado=integrado,
                    fecha=d[registro]['FECHA'],
                    codigo_camada=d[registro]['Código Camada'],
                    medicamentos=float(d[registro]['MEDICAMENTOS']),
                    liquidacion=float(d[registro]['LIQUIDACIÓN']),
                    pollos_entrados=float(d[registro]['Pollos Entrados']),
                    pollos_salidos=float(d[registro]['Pollos Salidos']),
                    porcentaje_bajas=float(d[registro]['% Bajas']),
                    bajas_primera_semana=float(d[registro]['BAJAS 1a. SEMANA']),
                    porcentaje_bajas_primera_semana=float(d[registro]['%BAJAS 1a. Semana']),
                    kilos_carne=float(d[registro]['Kilos Carne']),
                    kilos_pienso=float(d[registro]['Kilos Pienso']),
                    peso_medio=float(d[registro]['Peso Medio']),
                    indice_transformacion=float(d[registro]['I.Transform']),
                    retribucion=float(d[registro]['Retribución Pollo']),
                    medicamentos_por_pollo=float(d[registro]['Medic/Pollo']),
                    rendimiento_metro_cuadrado=float(d[registro]['Rdto/M2']),
                    pollo_metro_cuadrado=float(d[registro]['Pollo/Mt2']),
                    kilos_consumidos_por_pollo_salido=float(d[registro]['Kilos Consumidos por Pollo Salido']),
                    dias_media_retirada=float(d[registro]['Dias Media Retirada sin Asador']),
                    ganancia_media_diaria=float(d[registro]['Ganancia Media Diaria']),
                    dias_primer_camion=float(d[registro]['Días Primer Camión']),
                    peso_primer_dia=float(d[registro]['Peso 1 Día']),
                    peso_semana_1=float(d[registro]['Peso 1 Semana']),
                    peso_semana_2=float(d[registro]['peso 2 semana']),
                    peso_semana_3=float(d[registro]['peso 3 semana']),
                    peso_semana_4=float(d[registro]['peso 4 semana']),
                    peso_semana_5=float(d[registro]['peso 5 semana']),
                    peso_semana_6=float(d[registro]['peso 6 semana']),
                    peso_semana_7=float(d[registro]['peso 7 semana']),
                    # fecha=datetime.strptime(float(d[registro]['FECHA']), format="%d-%m-%Y"),
                    rendimiento=float(d[registro]['Rendimiento']),
                    FP=float(d[registro]['%  FP']),
                    bajas_matadero=float(d[registro]['Bajas']),
                    decomisos_matadero=float(d[registro]['Decomisos']),
                    porcentaje_bajas_matadero=float(d[registro]['% Bajas']),
                    porcentaje_decomisos=float(d[registro]['% Decomisos']),
                )
            except:
                pass

            if creado:
                RESULTADO_SUBIDA['n_camadas_subidas'] = (
                        RESULTADO_SUBIDA['n_camadas_subidas'] + 1)

    return True


def process_data(filename):
    """
    Dado el nombre de un archivo excel, cargar sus datos en la bd.
    El formato debe ser adecuado
    Debe
    """
    name, extension = os.path.splitext(filename)
    if extension == ".xlsx":  # Solo archivos excel
        data = pd.read_excel(filename)

    return data


def inicializar_resultados():

    RESULTADO_SUBIDA['nombre_provincia'] = set()
    RESULTADO_SUBIDA['nombre_tecnico'] = set()
    RESULTADO_SUBIDA['nombre_fabrica'] = set()
    RESULTADO_SUBIDA['nombre_poblacion'] = set()
    RESULTADO_SUBIDA['n_nombre_provincia'] = 0
    RESULTADO_SUBIDA['n_nombre_tecnico'] = 0
    RESULTADO_SUBIDA['n_nombre_fabrica'] = 0
    RESULTADO_SUBIDA['n_nombre_poblacion'] = 0

    RESULTADO_SUBIDA['n_camadas_subidas'] = 0
    RESULTADO_SUBIDA['n_integrados_subidos'] = 0

    RESULTADO_SUBIDA['n_total_registros_analizados'] = 0


def mostrar_resultados_subida():

    suma_errores = (
        RESULTADO_SUBIDA['n_nombre_provincia'] +
        RESULTADO_SUBIDA['n_nombre_tecnico'] +
        RESULTADO_SUBIDA['n_nombre_fabrica'] +
        RESULTADO_SUBIDA['n_nombre_poblacion']
    )

    """ Manda mensajes con flash, informando del resultado de la subida"""
    if (suma_errores > 0):
        flash("Se encontraron "+ str(suma_errores)
                + " errores con el nombre de fabrica. ", "warning")

        flash(
            Markup(
                "Puede resolver estos problemas modificando manualmente la tabla de entrada"
              + " o agregando estos nuevos valores al registro desde la "
              + " <a href=\"admin\" class=\"alert-link\">administracion. </a>"
              + "Contacte con el administrador si el problema persiste."
            )
              , "info"
        )

    # Copia los resultados actuales para presentarlos en la vista
    resultados_subida = dict(RESULTADO_SUBIDA)

    # Prepara el diccionario de resultados para una nueva búsqueda
    inicializar_resultados()

    return resultados_subida



def allowed_file(filename):
    """Comprueba si la extension del archivo es válida"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/load_data', methods=('GET', 'POST'))
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
                        if (RESULTADO_SUBIDA['n_camadas_subidas']
                                + RESULTADO_SUBIDA['n_integrados_subidos'] > 0):
                            flash(
                                "Se cargaron correctamente "
                                + str(RESULTADO_SUBIDA['n_camadas_subidas'])
                                + " camadas nuevas y "
                                + str(RESULTADO_SUBIDA['n_integrados_subidos'])
                                + " integrados nuevos."
                                ,"success"
                            )

                        # Se muestran los errores, camadas subidas...
                        resultado_subida = mostrar_resultados_subida()

                        return render_template('load_data.html',
                                               form=form,
                                               resultado_subida=resultado_subida,
                                               )

                        # return redirect(url_for('load_data'))
                    else:
                        flash('No se pudieron procesar los datos. Consulte con el administrador', "danger")
                    # va bien vuelve al index
                else:
                    flash('Extensión de fichero no válida', 'danger')


    # print("Antes: n_nombre_fabrica", RESULTADO_SUBIDA['n_nombre_fabrica'])

    return render_template('load_data.html', form=form, resultado_subida=RESULTADO_SUBIDA)  # Vuelve a intentarlo


# ==============================================================================
# TODO
    # Mostrar un resultado de la importación (camadas, integrados...)
