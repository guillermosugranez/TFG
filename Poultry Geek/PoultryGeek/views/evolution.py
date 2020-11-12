from flask import Blueprint

import sqlite3
import os
import time
from datetime import datetime, timedelta

from flask import (render_template)
from flask_login import (login_required)

import pandas as pd
import numpy as np
import matplotlib

from PoultryGeek.prediction.prediction import predecir

matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# App
from PoultryGeek import models
from PoultryGeek import CONFIGURACION
from PoultryGeek import g

bp = Blueprint(
    "evolution", __name__, template_folder='templates', static_folder='static')

# ==============================================================================


def min_max_year():

    # Se determina el año más alto y más bajo de los que se tengan camadas
    cnx = sqlite3.connect('social.db')
    # menor_fecha = cnx.execute("SELECT MIN(fecha) FROM camada").fetchone()[0]
    # mayor_fecha = cnx.execute("SELECT MAX(fecha) FROM camada").fetchone()[0]
    menor_fecha = models.Camada.get_fecha_primera_camada()
    mayor_fecha = models.Camada.get_fecha_ultima_camada()

    # print("La fecha menor es: ", menor_fecha)
    # print("La fecha mayor es: ", mayor_fecha)

    menor_anno = menor_fecha.year
    mayor_anno = mayor_fecha.year


    return menor_anno, mayor_anno


def graficos_evolucion(medias_variable, variable):


    plt.clf() # Se borra la imagen que huibiera anteriormente

    x = np.arange(0, len(medias_variable), 1)
    y = []

    # print(medias_variable)

    for media in medias_variable:
        y.append(media)

    plt.figure(figsize=(len(y)*0.6, 6))

    plt.grid(alpha=0.5)

    # Valores de x

    meses = [
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
    ]

    menor_anno, mayor_anno = min_max_year()

    lista_meses = []
    i = 0

    for mes in medias_variable:
        if i == 0:
            lista_meses.append(meses[i] + " " + str(menor_anno))
            menor_anno = menor_anno + 1
        else:
            lista_meses.append(meses[i])

        i = i + 1
        if i == 12:
            i = 0

    ruta_archivo_imagen = os.getcwd() + '/media/evolution_' + variable + '.svg'
    plt.xticks(ticks=x, labels=lista_meses, rotation=-45, horizontalalignment='left')
    plt.yticks(fontweight='bold')

    # ================                                          ================#
    # Gráfico de la predicción
    plt.plot(x, y, color="aqua")
    plt.plot(x, y, 'o', color="aqua")

    # ================                                          ================#
    # Gráfico de lo que llevamos hasta ahora (se le quita la media predicha)
    y.pop()
    x = np.arange(0, len(medias_variable)-1, 1)
    plt.plot(x, y, color=CONFIGURACION['variables_evolucion_tema'][variable])
    plt.plot(x, y, 'o',
             color=CONFIGURACION['variables_evolucion_tema'][variable])

    # ================                                          ================#
    # Formatea apropiadamente el resultado de la media predicha

    if variable == 'porcentaje_bajas':
        media_predicha = str(round(medias_variable.pop() * 100, 2)) + "%"
    else:
        media_predicha = str(medias_variable.pop().round(3))

    #================                                          ================#
    # Leyenda

    media_predicha_patch = mpatches.Patch(
        color='aqua',
        label="Media estimada para el mes siguiente:  " + media_predicha
    )

    legend_properties = {'weight': 'bold'}


    plt.legend(handles=[media_predicha_patch], prop=legend_properties)

    # ================                                          ================#
    # Guardar gráfico
    plt.savefig(ruta_archivo_imagen, orientation="landscape",
                bbox_inches="tight", pad_inches=0.2)


def calcular_medias_por_mes(lista_variables):
    """ Devuelve la media de cada mes del total de la integración,
    teniendo en cuenta las variables pasadas como parámetro """

    camadas = g.user.get_camadas()
    camadas = pd.DataFrame(list(camadas.dicts()))

    # camadas['fecha'] = pd.to_datetime(camadas["fecha"].index, unit='s')

    camadas['fecha'] = pd.to_datetime(camadas["fecha"])

    camadas = camadas.resample('M', on='fecha').mean()

    dict_variable_medias = {}

    for variable in lista_variables:
        lista = []
        for resultado in camadas[variable]:
            # print("El resultado es:", resultado)
            lista.append(resultado)
        dict_variable_medias[variable] = lista


    return dict_variable_medias


def info_tarjetas():
        """ Recolecta la información para mostrar en las tarjetas superiores"""

        informacion_tarjetas = {}

        # lista_campos = ['icono', 'tema']
        #
        #
        # for variable in CONFIGURACION['variables_evolucion']:
        #     for campo in lista_campos:

        # Ultima fecha
        try:
            ultima_fecha = models.Camada.get_fecha_ultima_camada()
            fecha_anterior = ultima_fecha - timedelta(days=365)
        except:
            return {}

        # print("tipo es: ", type(ultima_fecha))

        medias = {}

        for variable in CONFIGURACION['variables_evolucion']:

            medias[variable] = {}
            ultima = round(models.Camada.get_media(fecha=ultima_fecha, variable=variable), 3)
            anterior = round(models.Camada.get_media(fecha=fecha_anterior, variable=variable), 3)
            informacion_tarjetas[variable] = {'media_ultima': ultima, 'media_anterior': anterior}

        informacion_tarjetas['indice_transformacion']['icono'] = 'exchange-alt'
        informacion_tarjetas['peso_medio']['icono'] = 'balance-scale-right'
        informacion_tarjetas['porcentaje_bajas']['icono'] = 'percentage'
        informacion_tarjetas['retribucion']['icono'] = 'euro-sign'
        informacion_tarjetas['ganancia_media_diaria']['icono'] = 'coins'

        #=========                                                    =========#

        if (informacion_tarjetas['indice_transformacion']['media_ultima'] <
                informacion_tarjetas['indice_transformacion']['media_anterior']):
            informacion_tarjetas['indice_transformacion']['color'] = 'green'
        else:
            informacion_tarjetas['indice_transformacion']['color'] = 'red'


        if (informacion_tarjetas['peso_medio']['media_ultima'] >
                informacion_tarjetas['peso_medio']['media_anterior']):
            informacion_tarjetas['peso_medio']['color'] = 'green'
        else:
            informacion_tarjetas['peso_medio']['color'] = 'red'


        if (informacion_tarjetas['porcentaje_bajas']['media_ultima'] <
                informacion_tarjetas['porcentaje_bajas']['media_anterior']):
            informacion_tarjetas['porcentaje_bajas']['color'] = 'green'
        else:
            informacion_tarjetas['porcentaje_bajas']['color'] = 'red'


        if (informacion_tarjetas['retribucion']['media_ultima'] >
                informacion_tarjetas['retribucion']['media_anterior']):
            informacion_tarjetas['retribucion']['color'] = 'green'
        else:
            informacion_tarjetas['retribucion']['color'] = 'red'


        if (informacion_tarjetas['ganancia_media_diaria']['media_ultima'] <
                informacion_tarjetas['ganancia_media_diaria']['media_anterior']):
            informacion_tarjetas['ganancia_media_diaria']['color'] = 'green'
        else:
            informacion_tarjetas['ganancia_media_diaria']['color'] = 'red'

        # =========                                                    =========#

        informacion_tarjetas['ultima_fecha'] = datetime.strftime(
            ultima_fecha, "%d-%m-%Y")

        informacion_tarjetas['fecha_anterior'] = datetime.strftime(
            fecha_anterior,"%d-%m-%Y")

        # print(informacion_tarjetas)

        return informacion_tarjetas


@login_required
@bp.route('/evolution')
def evolution():
    """
    - Muestra la evolución de toda la integración.
    - Predice la media de las variables deseadas para el siguiente mes,
      y las incorpora al global.
    - Genera los gráficos correspondientes y los presenta en la web
    """

    # dict_variable_medias = calcular_medias_por_mes(CONFIGURACION["variables_evolucion"])
    try:
        dict_variable_medias = calcular_medias_por_mes(CONFIGURACION["variables_evolucion"])
    except:
        return render_template('evolution.html',
                               hay_datos=False,
                               informacion_tarjetas=info_tarjetas(),
                               tema=CONFIGURACION['variables_evolucion_tema'],
                               variables_evolucion=(
                                   CONFIGURACION["variables_evolucion"]),
                               url_variable=(
                                   time.strftime("%Y%m%d%H%M%S"))
                               )


    # for anno in medias:
    #     print(anno)
    #     for variable in medias[anno]:
    #         print(variable)
    #         for media in medias[anno][variable]:
    #             print(media)

    dict_variable_medias = predecir(dict_variable_medias)

    for variable in dict_variable_medias:
        graficos_evolucion(dict_variable_medias[variable], variable)


    return render_template('evolution.html',
                           hay_datos=True,
                           informacion_tarjetas=info_tarjetas(),
                           tema=CONFIGURACION['variables_evolucion_tema'],
                           variables_evolucion=(
                               CONFIGURACION["variables_evolucion"]),
                           url_variable=(
                               time.strftime("%Y%m%d%H%M%S"))
                           )


# ==============================================================================
# TODO

    # Detectar si ha habido cambios