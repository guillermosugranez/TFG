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

# FUNCIONES CHECK
# Estas funciones se encargan de:
# - Comprobar que los nombres de los atributos de las camadas (provincia,
# tecnico...) estén ya en bbdd y, que por tanto, pueda añadirse la camada
# - Si no están los apuntan el error mediante contadores y conjuntos.
# - Estos resultados son registrados en RESULTADO_SUBIDA


RESULTADO_SUBIDA = {
    'nombre_provincia'              : set(),
    'nombre_tecnico'                : set(),
    'nombre_fabrica'                : set(),
    'nombre_poblacion'              : set(),

    'n_nombre_provincia'            : 0,
    'n_nombre_tecnico'              : 0,
    'n_nombre_fabrica'              : 0,
    'n_nombre_poblacion'            : 0,

    'n_total_registros_analizados'  : 0,

    'n_camadas_subidas'             : 0,
    'n_integrados_subidos'          : 0,

    'n_errores_camada'              : 0,
    'n_errores_integrado'           : 0,

    'lineas_error'                  : []
}

def inicializar_resultados():

    # Conjuntos vacíos
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

    RESULTADO_SUBIDA['n_errores_camada'] = 0
    RESULTADO_SUBIDA['n_errores_integrado'] = 0

    RESULTADO_SUBIDA['n_total_registros_analizados'] = 0
    RESULTADO_SUBIDA['lineas_error'] = []


def check_provincia(nombre_provincia):

    if nombre_provincia.strip().title() in models.Provincia.get_list_provincias():
        return True
    else:
        # print("nombre provincia no valido")

        # Se añade al conjunto de provincias no registradas
        RESULTADO_SUBIDA['nombre_provincia'].add(
            nombre_provincia.strip().title()
        )

        # Se cuenta como un error más
        RESULTADO_SUBIDA['n_nombre_provincia'] = (
            RESULTADO_SUBIDA['n_nombre_provincia'] + 1
        )

        return False


def check_fabrica(nombre_fabrica):

    if nombre_fabrica.strip().title() in models.Fabrica.get_list_fabricas():
        return True
    else:

        # print("fabrica no valido")
        RESULTADO_SUBIDA['nombre_fabrica'].add(
            nombre_fabrica.strip().title()
        )

        RESULTADO_SUBIDA['n_nombre_fabrica'] = (
            RESULTADO_SUBIDA['n_nombre_fabrica'] + 1
        )

        # print("Check: n_nombre_fabrica",
        #       RESULTADO_SUBIDA['n_nombre_fabrica'])

        return False


def check_poblacion(nombre_poblacion):

    if nombre_poblacion.strip().title() in models.Poblacion.get_list_poblaciones():
        return True
    else:
        # print("poblacion no valido")

        # print("fabrica no valido")
        RESULTADO_SUBIDA['nombre_poblacion'].add(
            nombre_poblacion.strip().title()
        )

        RESULTADO_SUBIDA['n_nombre_poblacion'] = (
            RESULTADO_SUBIDA['n_nombre_poblacion'] + 1
        )

        return False


def check_tecnico(nombre_tecnico):

    if nombre_tecnico.strip().title() in models.Tecnico.get_list_tecnicos():
        return True
    else:
        # print("tecnico no valido")

        # Se añade al conjunto de técnicos no registrados
        RESULTADO_SUBIDA['nombre_tecnico'].add(
            nombre_tecnico.strip().title()
        )

        # Se cuenta como un error más
        RESULTADO_SUBIDA['n_nombre_tecnico'] = (
                RESULTADO_SUBIDA['n_nombre_tecnico'] + 1
        )

        return False


def check_fecha(fecha):
    """
    Comprueba si el formato de la fecha es correcto
    y si está en un intervalo válido
    """
    # print("el tipo de la fecha es: ", type(fecha))
    # print("La fecha es: ", fecha)

    # Solo datos comprendidos entre 2015 y la fecha actual
    try:
        if (
                (fecha > datetime.strptime("2014-12-31", "%Y-%m-%d"))
                &
                (fecha <= datetime.today())
        ):
            return True
        else:
            RESULTADO_SUBIDA['n_errores_camada'] = (
                    RESULTADO_SUBIDA['n_errores_camada'] + 1
            )
            return False
    except:
        RESULTADO_SUBIDA['n_errores_camada'] = (
                RESULTADO_SUBIDA['n_errores_camada'] + 1
        )
        return False


def dataset_to_bd(dataframe):
    """Procesa la información de un dataset y trata de guardarla en la bbdd"""

    tabla = dataframe.to_dict('index')
    creado = False
    linea = 1

    for registro in tabla:

        linea = linea + 1

        RESULTADO_SUBIDA['n_total_registros_analizados'] = (
            RESULTADO_SUBIDA['n_total_registros_analizados'] + 1
        )

        nombres_correctos = True

        # Se validan los datos. Si falla salta el registro:

        #============#                                            #============#

        nombres_correctos = (nombres_correctos
                          * check_provincia(tabla[registro]['Provincia'])
                          * check_tecnico(tabla[registro]['Técnico'])
                          * check_fabrica(tabla[registro]['Fab. Pienso'])
                          * check_poblacion(tabla[registro]['Población'])
                           )

        # Los dos errores no son incompatibles
        if not nombres_correctos:
            RESULTADO_SUBIDA['lineas_error'].append(
                {str(linea) : "Nombre incorrecto o no registrado."})

        #============#                                            #============#

        fecha_valida = check_fecha(tabla[registro]['FECHA'])

        if not fecha_valida:
            RESULTADO_SUBIDA['lineas_error'].append(
                {str(linea) : "Fecha no válida."})

        # ============#                                            #============#

        # Trata de introducir el registro en bbdd
        if nombres_correctos & fecha_valida:
            try:
                # Cojo la provincia que ya está en bbdd
                provincia = models.Provincia.get(
                    models.Provincia.nombre_provincia **
                    (tabla[registro]['Provincia'].strip().title()))

                tecnico = models.Tecnico.get(
                    models.Tecnico.nombre_tecnico **
                    (tabla[registro]['Técnico'].strip().title()))

                fabrica = models.Fabrica.get(
                    models.Fabrica.nombre_fabrica **
                    (tabla[registro]['Fab. Pienso'].strip().title()))

                poblacion = models.Poblacion.get(
                    models.Poblacion.nombre_poblacion **
                    (tabla[registro]['Población'].strip().title()))

                # Se crea el integrado
                creado = models.Integrado.create_integrado(
                    user=g.user._get_current_object(),
                    tecnico=tecnico,
                    fabrica=fabrica,
                    codigo=tabla[registro]['Código'],
                    nombre_integrado=tabla[registro]['Avicultor'].strip().title(),
                    poblacion=poblacion,
                    provincia=provincia,
                    ditancia=tabla[registro]['Distancia a Matadero Purullena'],
                    metros_cuadrados=tabla[registro]['Mts Cuadrados'],
                )

                # Se apunta el número de integrados creados en el proceso
                if creado == "ok":
                    RESULTADO_SUBIDA['n_integrados_subidos'] = (
                            RESULTADO_SUBIDA['n_integrados_subidos'] + 1)
                elif creado == "existe":
                    # print("existe")
                    # No se considera tan relevante porque es repetitivo
                    pass
                elif creado == "error":
                    # print("error")
                    RESULTADO_SUBIDA['n_errores_integrado'] = (
                            RESULTADO_SUBIDA['n_errores_integrado'] + 1)
                    pass

                # ==================================================================

                # Cojo el integrado que ya está en bbdd
                integrado = models.Integrado.get(
                    models.Integrado.nombre_integrado **
                    tabla[registro]['Avicultor'].strip().title())

                # Se crea la camada

                creado = models.Camada.create_camada(
                    integrado=integrado,
                    fecha=tabla[registro]['FECHA'],
                    codigo_camada=tabla[registro]['Código Camada'],

                    pollos_entrados=float(tabla[registro]['Pollos Entrados']),
                    pollos_salidos=float(tabla[registro]['Pollos Salidos']),
                    porcentaje_bajas=float(tabla[registro]['% Bajas']),
                    kilos_carne=float(tabla[registro]['Kilos Carne']),
                    kilos_pienso=float(tabla[registro]['Kilos Pienso']),
                    peso_medio=float(tabla[registro]['Peso Medio']),
                    indice_transformacion=float(tabla[registro]['I.Transform']),
                    retribucion=float(tabla[registro]['Retribución Pollo']),
                    medicamentos_por_pollo=float(tabla[registro]['Medic/Pollo']),
                    ganancia_media_diaria=float(tabla[registro]['Ganancia Media Diaria']),
                    dias_media_retirada=float(tabla[registro]['Dias Media Retirada sin Asador']),

                    medicamentos=tabla[registro]['MEDICAMENTOS'],
                    liquidacion=tabla[registro]['LIQUIDACIÓN'],
                    bajas_primera_semana=tabla[registro]['BAJAS 1a. SEMANA'],
                    porcentaje_bajas_primera_semana=tabla[registro]['%BAJAS 1a. Semana'],
                    rendimiento_metro_cuadrado=tabla[registro]['Rdto/M2'],
                    pollo_metro_cuadrado=tabla[registro]['Pollo/Mt2'],
                    kilos_consumidos_por_pollo_salido=tabla[registro]['Kilos Consumidos por Pollo Salido'],
                    dias_primer_camion=tabla[registro]['Días Primer Camión'],
                    peso_primer_dia=tabla[registro]['Peso 1 Día'],
                    peso_semana_1=tabla[registro]['Peso 1 Semana'],
                    peso_semana_2=tabla[registro]['peso 2 semana'],
                    peso_semana_3=tabla[registro]['peso 3 semana'],
                    peso_semana_4=tabla[registro]['peso 4 semana'],
                    peso_semana_5=tabla[registro]['peso 5 semana'],
                    peso_semana_6=tabla[registro]['peso 6 semana'],
                    peso_semana_7=tabla[registro]['peso 7 semana'],
                    rendimiento=tabla[registro]['Rendimiento'],
                    FP=tabla[registro]['%  FP'],
                    bajas_matadero=tabla[registro]['Bajas'],
                    decomisos_matadero=tabla[registro]['Decomisos'],
                    porcentaje_bajas_matadero=tabla[registro]['% Bajas'],
                    porcentaje_decomisos=tabla[registro]['% Decomisos'],
                )

                # Se apunta el numero de camadas creadas en el proceso
                if creado == "ok":
                    RESULTADO_SUBIDA['n_camadas_subidas'] = (
                            RESULTADO_SUBIDA['n_camadas_subidas'] + 1)
                elif creado == "existe":
                    # print("existe")
                    RESULTADO_SUBIDA['n_errores_camada'] = (
                            RESULTADO_SUBIDA['n_errores_camada'] + 1
                    )
                    RESULTADO_SUBIDA['lineas_error'].append(
                        {str(linea): "Esta camada ya existe."})
                    pass
                elif creado == "error":
                    # print("error")
                    RESULTADO_SUBIDA['n_errores_camada'] = (
                            RESULTADO_SUBIDA['n_errores_camada'] + 1
                    )
                    RESULTADO_SUBIDA['lineas_error'].append({str(linea) : "Error en el valor de los datos"})
                    pass
            except:
                RESULTADO_SUBIDA['lineas_error'].append({str(linea) : "Error desconocido."})
                pass

    # if len(RESULTADO_SUBIDA['lineas_error']) > 0:
    #     for linea in RESULTADO_SUBIDA['lineas_error']:
    #         print(linea)

    # Esto determina si hubo registros analizados
    if RESULTADO_SUBIDA['n_total_registros_analizados']:
        return True
    else:
        return False


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


def mostrar_resultados_subida():

    suma_errores = (
        RESULTADO_SUBIDA['n_nombre_provincia'] +
        RESULTADO_SUBIDA['n_nombre_tecnico'] +
        RESULTADO_SUBIDA['n_nombre_fabrica'] +
        RESULTADO_SUBIDA['n_nombre_poblacion']
    )

    errores = 0

    print("n_errores_integrado", RESULTADO_SUBIDA['n_errores_integrado'])
    print("n_errores_camada", RESULTADO_SUBIDA['n_errores_camada'])

    # Manda mensajes con flash, informando del resultado de la subida
    if RESULTADO_SUBIDA['n_errores_integrado'] or RESULTADO_SUBIDA['n_errores_camada']:
        flash("Debido a errores en los datos, no se pudieron incluir "
              + str(RESULTADO_SUBIDA['n_errores_integrado'])
              + " integrado/s y "
              + str(RESULTADO_SUBIDA['n_errores_camada'])
              + " camada/s."
              ,"warning")

    # Manda mensajes con flash, informando del resultado de la subida
    if (suma_errores):
        flash("Se han encontrado "
              + str(suma_errores)
              + " errores de nombres no registrados."
              + " Consulte las tablas de más abajo para más información."
              ,"warning"
        )

    # Si existen errores de cualquier tipo manda un mensaje de ayuda
    if suma_errores or RESULTADO_SUBIDA['n_errores_integrado'] or RESULTADO_SUBIDA['n_errores_camada']:
        flash(
            Markup(
                "Puede tratar de resolver estos problemas modificando manualmente la tabla de entrada"
              + " o también, en el caso concreto de que haya nombres no registrados, agregarlos al registro desde la "
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
                        flash(
                            "Se han analizado "
                            + str(RESULTADO_SUBIDA['n_total_registros_analizados'])
                            + " registros.",
                            "info"
                        )
                        if RESULTADO_SUBIDA['n_camadas_subidas'] + RESULTADO_SUBIDA['n_integrados_subidos'] > 0:
                            flash(
                                "Se cargaron correctamente "
                                + str(RESULTADO_SUBIDA['n_camadas_subidas'])
                                + " camadas nuevas y "
                                + str(RESULTADO_SUBIDA['n_integrados_subidos'])
                                + " integrados nuevos.",
                                "success"
                            )

                        # Se muestran los errores, camadas subidas...
                        # La función copia los resultados y los inicializa
                        resultado_subida = mostrar_resultados_subida()

                        return render_template(
                            'load_data.html',
                            form=form,
                            resultado_subida=resultado_subida,
                            variables=CONFIGURACION[
                                'variables_comprobacion_subida']
                        )

                        # return redirect(url_for('load_data'))
                    else:
                        flash('No se pudieron procesar los datos. Consulte con el administrador', "danger")
                    # va bien vuelve al index
                else:
                    flash('Extensión de fichero no válida', 'danger')


    # print("Antes: n_nombre_fabrica", RESULTADO_SUBIDA['n_nombre_fabrica'])

    return render_template(
        'load_data.html',
        form=form,
        resultado_subida=RESULTADO_SUBIDA,
        variables=CONFIGURACION['variables_comprobacion_subida']
    )  # Vuelve a intentarlo


# ==============================================================================
# TODO
    # Mostrar un resultado de la importación (camadas, integrados...)
