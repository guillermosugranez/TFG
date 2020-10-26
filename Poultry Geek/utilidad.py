from peewee import fn
import pandas as pd
import sqlite3

from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

"""
    Todas las funciones que sirven a las vistas
"""
import models

def graficos_evolucion(medias_variable, variable):

    plt.clf()
    t = np.arange(0, 3*len(medias_variable), 1)
    v = []

    for media in medias_variable:
        v.append(media)

    for media in medias_variable:
        v.append(media)

    for media in medias_variable:
        v.append(media)

    plt.figure(figsize=(14, 6))

    plt.plot(t, v, color="aqua")
    v.pop()
    t = np.arange(0, 3*len(medias_variable)-1, 1)
    plt.plot(t, v, color="green")

    # ax.set(xlabel='time (s)', ylabel='voltage (mV)',
    #        title=variable)
    # ax.grid()
    #
    # ax.set_size_inches(14, 6)
    #
    ruta_archivo_imagen = os.getcwd() + '/media/evolution_' + variable + '.svg'

    plt.savefig(ruta_archivo_imagen, orientation="landscape",
                bbox_inches="tight", pad_inches=0.2)


def obtener_valores(lista_variables):
    """ Devuelve la media de cada mes del total de la integración,
    teniendo en cuenta las variables pasadas como parámetro """

    # avicultores = models.Integrado.select(
    #     models.Integrado.nombre_integrado).execute()

    # Se forma la consulta:

    # valores_variables = models.Integrado.select(
    #     models.Integrado.nombre_integrado).execute()

    # avicultores = models.Integrado.select(models.Integrado.nombre_integrado).execute()


    valores = {}
    cnx = sqlite3.connect('social.db')

    # Se construye un diccionario (key: variable, value: dataframe con valores)
    for variable in lista_variables:
        consulta = "SELECT " + variable + " FROM camada"
        df_variable = pd.read_sql_query(consulta, cnx)
        valores[variable] = df_variable

    return valores
    # Se recibe un diccionario con las variables y una lista con sus medias

    # Se devuelve para su presentación en la plantilla

def calcular_medias_por_mes(lista_variables):
    """ Devuelve la media de cada mes del total de la integración,
    teniendo en cuenta las variables pasadas como parámetro """

    cnx = sqlite3.connect('social.db')

    menor_fecha = cnx.execute("SELECT MIN(fecha) FROM camada").fetchone()[0]
    mayor_fecha = cnx.execute("SELECT MAX(fecha) FROM camada").fetchone()[0]

    menor_anno = datetime.strptime(menor_fecha, "%Y-%m-%d").year
    mayor_anno = datetime.strptime(mayor_fecha, "%Y-%m-%d").year

    print(menor_anno)
    print(mayor_anno)


    medias = {} # guarda las medias de cada mes de cada año de cada variable

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
        camadas = camadas.groupby(camadas['fecha'].dt.month).mean() # por meses

        # Pora cada variable de cada año se coge la media de sus meses
        for variable in lista_variables:
            medias_anno_actual[variable] = camadas[variable]
            medias[str(anno)] = medias_anno_actual

    # print("\nmedias:\n", medias)

    return medias