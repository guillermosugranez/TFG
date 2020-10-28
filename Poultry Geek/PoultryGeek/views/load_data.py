from flask import Blueprint

import os
import time

from flask import (g, render_template, flash, url_for, redirect, request)
from flask_login import (login_required)
from werkzeug.utils import secure_filename # Importar archivos

import pandas as pd

# App
from PoultryGeek import CONFIGURACION
from PoultryGeek import app
from PoultryGeek import forms
from PoultryGeek import models


ALLOWED_EXTENSIONS = {'xlsx'}

bp = Blueprint("load_data", __name__, template_folder='templates', static_folder='static')


# ==============================================================================


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
                models.Integrado.nombre_integrado **
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
                        flash("Datos cargados con éxito", "success")
                        return render_template('evolution.html',
                                               variables_evolucion=CONFIGURACION["variables_evolucion"],
                                               url_variable=time.strftime(
                                                   "%Y%m%d%H%M%S")
                                               )

                        return redirect(url_for('evolution'))
                    else:
                        flash('No se pudieron procesar los datos', "danger")
                    # va bien vuelve al index
                else:
                    flash('Extensión de fichero no válida', 'danger')

    return render_template('load_data.html', form=form)  # Vuelve a intentarlo


# ==============================================================================
# TODO
    # Mostrar un resultado de la importación (camadas, integrados...)
