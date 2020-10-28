from flask import Blueprint

import sqlite3
import os
import time
from datetime import datetime

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


def graficos_evolucion(medias_variable, variable):

    plt.clf() # Se borra la imagen que huibiera anteriormente

    x = np.arange(0, len(medias_variable), 1)
    y = []

    print(medias_variable)

    for media in medias_variable:
        y.append(media)

    plt.figure(figsize=(len(y)*0.5, 6))

    plt.grid(alpha=0.5)

    # Gráfico de la predicción
    plt.plot(x, y, color="aqua")

    # Gráfico de lo que llevamos hasta ahora (se le quita la media predicha)
    y.pop()
    x = np.arange(0, len(medias_variable)-1, 1)
    plt.plot(x, y, color="green")

    # Valores de x (meses)

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
    cnx = sqlite3.connect('social.db')
    menor_fecha = cnx.execute("SELECT MIN(fecha) FROM camada").fetchone()[0]
    mayor_fecha = cnx.execute("SELECT MAX(fecha) FROM camada").fetchone()[0]

    menor_anno = datetime.strptime(menor_fecha, "%Y-%m-%d").year
    mayor_anno = datetime.strptime(mayor_fecha, "%Y-%m-%d").year

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

    lista_valores_y = []
    lista_valores_x = []

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
        lista_valores_y.append(conjunto_y)

    # Se concatenan las tablas de los valores x
    tabla_final = pd.concat(lista_valores_x, axis='columns')

    # print("La tabla final al principio\n\n", tabla_final)

    # Se saca el patron a predecir:
    patron_a_predecir = tabla_final.tail(1)  # Se trata del último patron
    # print("patron a predecir" + str(patron_a_predecir.shape) + ". \n", patron_a_predecir)

    # Una vez sacado el patron a predecir, se elimina de la tabla final
    tabla_final = tabla_final.iloc[:-1]

    # print("La tabla final:\n\n", tabla_final)

    return lista_valores_y, tabla_final, patron_a_predecir


def predecir(variables_a_predecir):
    """ Predice la media del mes siguiente para un conjunto de variables """

    dict_variable_medias = {}

    medias = calcular_medias_por_mes(variables_a_predecir)

    # Inicializo las listas para añadirles elementos
    for variable in variables_a_predecir:
        dict_variable_medias[variable] = []

    # Se prepara el formato para el proceso
    for anno in medias:
        for variable in medias[anno]:
            # print(medias[anno][variable])
            for mes in medias[anno][variable]:
                dict_variable_medias[variable].append(mes)

    # print(dict_variable_medias)

    # m0 = [9, 8, 7, 7, 7, 5, 3, 5, 5, 6, 7, 4, 5, 7, 5, 4, 3, 5, 6, 7, 8, 5]
    # m1 = [9, 8, 7, 2, 7, 3, 7, 5, 8, 6, 4, 2, 2, 1, 9, 4, 3, 1, 3, 2, 8, 1]

    # # Esto es lo que hay que pasarle
    # dict_variable_medias = {
    #     'pollos_entrados': m0,
    #     'pollos_salidos': m1,
    # }

    # Se obtiene el modelo autoregresivo con las medias calculadas
    lista_valores_y, tabla_final, patron_a_predecir = (
        modelo_autoregresivo(
            dict_variable_medias,
            num_variables_lag=3
        )
    )

    # ==========================================================================

    # Se aplica el modelo que se haya determinado
    regr = linear_model.LinearRegression()
    medias_predichas = [] # Aqui se van guardando las medias predichas

    # Se hace para cada una de las variables
    for y_variable in lista_valores_y:
        # Se usan todos los datos disponibles para predecir
        regr.fit(tabla_final, y_variable)
        y_pred = regr.predict(patron_a_predecir)
        medias_predichas.append(y_pred[0][0])

    # print(medias_predichas)

    # Se añaden a las medias y se genera el gráfico correspondiente
    i = 0
    for variable in dict_variable_medias:
        dict_variable_medias[variable].append(medias_predichas[i])
        i = i + 1
        # print(dict_variable_medias[variable])
        graficos_evolucion(dict_variable_medias[variable], variable)


@login_required
@bp.route('/evolution')
def evolution():
    """
    - Muestra la evolución de toda la integración.
    - Predice la media de las variables deseadas para el siguiente mes,
      y las incorpora al global.
    - Genera los gráficos correspondientes y los presenta en la web
    """

    # Se aplicará la predicción a las variables definidas en la configuración
    predecir(CONFIGURACION["variables_evolucion"])

    return render_template('evolution.html',
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