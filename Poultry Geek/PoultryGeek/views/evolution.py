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
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Predicción
from sklearn import linear_model

# App
from PoultryGeek import models
from PoultryGeek import CONFIGURACION

bp = Blueprint(
    "evolution", __name__, template_folder='templates', static_folder='static')


# ==============================================================================


def min_max_year():

    # Se determina el año más alto y más bajo de los que se tengan camadas
    cnx = sqlite3.connect('social.db')
    menor_fecha = cnx.execute("SELECT MIN(fecha) FROM camada").fetchone()[0]
    mayor_fecha = cnx.execute("SELECT MAX(fecha) FROM camada").fetchone()[0]

    # print("La fecha menor es: ", menor_fecha)
    # print("La fecha mayor es: ", mayor_fecha)

    menor_anno = datetime.strptime(menor_fecha, "%Y-%m-%d").year
    mayor_anno = datetime.strptime(mayor_fecha, "%Y-%m-%d").year


    return menor_anno, mayor_anno


def graficos_evolucion(medias_variable, variable):


    plt.clf() # Se borra la imagen que huibiera anteriormente

    x = np.arange(0, len(medias_variable), 1)
    y = []

    # print(medias_variable)

    for media in medias_variable:
        y.append(media)

    plt.figure(figsize=(len(y)*0.5, 6))

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

    plt.xticks(ticks=x, labels=lista_meses, rotation=-45, horizontalalignment='left')

    # Gráfico de la predicción
    plt.plot(x, y, color="aqua")

    # Gráfico de lo que llevamos hasta ahora (se le quita la media predicha)
    y.pop()
    x = np.arange(0, len(medias_variable)-1, 1)
    plt.plot(x, y, color=CONFIGURACION['variables_evolucion_tema'][variable])

    # Valores de x (meses)



    # plt.xlabel()

    # ax.set(xlabel='time (s)', ylabel='voltage (mV)',
    #        title=variable)
    # ax.grid()
    #
    # ax.set_size_inches(14, 6)
    #
    ruta_archivo_imagen = os.getcwd() + '/media/evolution_' + variable + '.svg'

    plt.savefig(ruta_archivo_imagen, orientation="landscape",
                bbox_inches="tight", pad_inches=0.2)


def calcular_medias_por_mes(lista_variables):
    """ Devuelve la media de cada mes del total de la integración,
    teniendo en cuenta las variables pasadas como parámetro """

    # Se determina el año más alto y más bajo de los que se tengan camadas
    menor_anno, mayor_anno = min_max_year()

    # print(menor_anno)
    # print(mayor_anno)

    medias = {} # guarda las medias de cada mes de cada año de cada variable

    # Por cada año, se obtiene la media de la variable de cada mes
    for anno in range(menor_anno, mayor_anno+1, 1):
        medias_anno_actual = {}
        query = (
            models.Camada
            .select()
            .where(
                (models.Camada.fecha > str(anno) + "-01-01") &
                (models.Camada.fecha < str(anno) + "-12-31")
            )
            .order_by(models.Camada.fecha)
        )

        camadas = pd.DataFrame(list(query.dicts()))

        # Se convierte primero a datetime (pandas usa Timestamp)
        camadas["fecha"] = pd.to_datetime(camadas["fecha"])

        # Se agrupan los resultados por mes y se hace la media por mes
        camadas = camadas.groupby(camadas['fecha'].dt.month).mean()

        # Por cada variable de cada año se coge la media de sus meses
        for variable in lista_variables:
            medias_anno_actual[variable] = camadas[variable]
            medias[str(anno)] = medias_anno_actual

    # print("\nmedias:\n", medias)

    return medias


def modelo_autoregresivo(dict_variable_medias, num_variables_lag=3):
    """
    Prepara una serie de valores para que pueda ser predicho el siguiente
    elemento de la serie por un algoritmo de regresión.

    Recibe:
    - Diccionario con las medias de cada variable y por cada mes
    anterior al actual.
    - El número de variables lag que se deben incluir (por defecto 3)

    Devuelve:
    - La tabla final con los valores de x
    - Sus correspondientes valores y
    - El patrón a predecir
    """

    lista_valores_x = [] # Con ellos se forma la tabla final (concat)

    # Para cada variable se guarda su conjunto 'y' particular
    valores_y_de_cada_variable = {}

    for variable in dict_variable_medias.keys():
        # print(variable)

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

        # print("\nLa tabla antes de ser capada\n", tabla_de_variable)

        # Se forma el conjunto de resultados (columna y)
        y = pd.DataFrame(
            dict_variable_medias[variable],
            columns=["y"]
        )
        y = y.shift(periods=-1)  # Se desplaza una posición hacia arriba

        # print("\nConjunto y: ", y)
        # print("La tabla original\n", tabla, y)

        # Se quitan las filas con valores NaN (Se capa por arriba).
        conjunto_x = tabla_de_variable[num_variables_lag:]  # tanto en la tabla
        conjunto_y = y[num_variables_lag:]  # como en la columna de resultados

        # Se elimina el último resultado de 'y' (NaN)
        conjunto_y = conjunto_y.iloc[:-1]

        # Se añade este conjunto para posteriormente poder predecir la variable
        lista_valores_x.append(conjunto_x)  # A concat se le pasa una fila
        # Se añade al diccionario la columna y correspondiente
        valores_y_de_cada_variable[variable] = conjunto_y

    # Se concatenan las tablas de los valores x
    tabla_final = pd.concat(lista_valores_x, axis='columns')

    # print("La tabla final al principio\n\n", tabla_final)

    # Se saca el patron a predecir:
    patron_a_predecir = tabla_final.tail(1)  # Se trata del último patron
    # print("patron a predecir" + str(patron_a_predecir.shape) + ". \n", patron_a_predecir)

    # Una vez sacado el patron a predecir, se elimina de la tabla final
    tabla_final = tabla_final.iloc[:-1]

    # print("La tabla final:\n\n", tabla_final)

    return valores_y_de_cada_variable, tabla_final, patron_a_predecir


def predecir(variables_a_predecir, medias):
    """
    Predice la media del mes siguiente para un conjunto de variables

    * Recibe:
        - Diccionario con las medias por meses de cada variable

    * Devuelve:
        - Mismo diccionario con la media del mes siguiente predicha

    """

    dict_variable_medias = {}

    # Inicializo las listas para añadirles elementos
    for variable in variables_a_predecir:
        dict_variable_medias[variable] = []

    # Se prepara el formato para el proceso
    # Se comprubea que no haya meses sin datos
    for anno in medias:
        for variable in medias[anno]:
            # print(medias[anno][variable])
            for mes in range(1, 13, 1):
                try:
                    dict_variable_medias[variable].append(medias[anno][variable][mes])
                except:
                    # Tiene que mostrar un error si no hay datos entre los meses
                    # print("te muestro un error")
                    # No pintar las gráficas
                    pass
                else:
                    # print("Dato bien registrado")
                    pass
            print("")

            # for mes in medias[anno][variable]:
            #     print("mes: ", mes)
            #

    # Se obtiene el modelo autoregresivo con las medias calculadas
    valores_y_de_cada_variable, tabla_final, patron_a_predecir = (
        modelo_autoregresivo(
            dict_variable_medias,
            num_variables_lag=3
        )
    )

    # ==========================================================================

    # Se aplica el modelo que se haya determinado
    regr = linear_model.LinearRegression()

    # Se predice el siguiente mes para cada variable
    for variable in dict_variable_medias:
        regr.fit(tabla_final, valores_y_de_cada_variable[variable])
        media_predicha = regr.predict(patron_a_predecir)
        dict_variable_medias[variable].append(media_predicha[0][0])
        # print(dict_variable_medias[variable])

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

        print(informacion_tarjetas)

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

    try:
        medias = calcular_medias_por_mes(CONFIGURACION["variables_evolucion"])
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


    # Se aplicará la predicción a las variables definidas en la configuración
    dict_variable_medias = predecir(CONFIGURACION["variables_evolucion"], medias)

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
    # Normalizar los xs y los ys minmax()
    # Después habría que desnormalizar el resultado

    # SVM para regresion
    # perceptron multicapa para regresion
    # procesos gausianos

    # Detectar si ha habido cambios

    # Sección de pruebas (fijarse en el proyecto arena) (20-30)
    # Sección de resultados (Es donde debería ir este estudio)

    # grid search (ajuste de hiperparámetro)

    # Preguntar a Pedro por el tipo de modelo

    # Manejar el problema de los meses

    # Problema si el año empieza en otro mes que no es enero (graficos)