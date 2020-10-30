from flask import Blueprint

import os
import math
import time
from datetime import datetime

from flask import (render_template, url_for, redirect, request)
from flask_login import (login_required,
                         current_user)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# App
from PoultryGeek import models
from PoultryGeek import forms
from PoultryGeek import CONFIGURACION

bp = Blueprint("table", __name__, template_folder='templates', static_folder='static')


# ==============================================================================


def numero_dias_intervalo(desde, hasta):

    # print("Desde: ", desde)
    # print("Hasta: ", hasta)

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

    # print(periodos)

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

        if math.isnan(media): # Si el valor es NaN
            medias.append(ultimo_valido)
        else:
            medias.append(media)
            ultimo_valido = media


    # print(medias)



    # medias = a.rolling(
    #     window=3
    # ).mean()

    # medias = pd.rolling_mean(
    #     arg = table["pollos_entrados"],
    #     window=3
    # )
    return medias


def search_function(query_params):
    """Devuelve un dataframe con la consulta realizada"""

    # print("desde: ", query_params["desde"])
    # print("hasta: ", query_params["hasta"])

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


@login_required
@bp.route('/search', methods=('GET', 'POST'))
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
                    format((f'{table[variable].mean():,.3f}')).replace(',','~').replace('.', ',').replace('~', '.')
                )
                lista_por_variable.append(
                    format((f'{table[variable].std():,.3f}')).replace(',','~').replace('.', ',').replace('~', '.')
                )


            estadisticas[variable] = lista_por_variable

    # print(estadisticas)

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
    avicultores = models.Integrado.select(
        models.Integrado.nombre_integrado).execute()

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
            # print("Las medias son: ", medias)
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
@bp.route('/table', methods=('GET', 'POST'))
def table():
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


# ==============================================================================
# TODO