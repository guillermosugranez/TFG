import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from statsmodels.tsa.statespace.sarimax import SARIMAX


import pandas as pd



if __name__ == "__main__":
    """
    Entorno de pruebas para probar los algoritmos
    - Se pasa un diccionario con el nombre de la variable y sus medias
    - Para cada variable se hace, sin valores NaN, la matriz y su vector 'y'
    - Se concatenan formando una única matriz
    - Por cada variable que se desee predecir:
        - Se genera el modelo con la matriz y el correspondiente valor y
        - Se predice con el patron resultante
        - Se repite el proceso hasta que no queden variables
    """

    # Lista de parámetros:
    intervalo = 0
    num_variables_lag = 4

    m0 = [9, 8, 7, 7, 7, 5, 3, 5, 5, 6, 7, 4, 5, 7, 5, 4, 3, 5, 6, 7, 8, 5]
    m1 = [9, 8, 7, 2, 7, 3, 7, 5, 8, 6, 4, 2, 2, 1, 9, 4, 3, 1, 3, 2, 8, 1]

    dict_variable_medias = {
        'pollos_entrados' : m0,
        'pollos_salidos': m1,
    }

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
            tabla_de_variable.insert(i+1,(variable + "_t-" + str(i+1)), dataframe_medias)
    #
        # Se forma el conjunto de resultados (columna y)
        y = pd.DataFrame(
            dict_variable_medias[variable],
            columns=["y"]
        )
        y = y.shift(periods=-1) # Se desplaza una posición hacia arriba

        # print("La tabla original\n", tabla, y)

        # Se quitan las filas con valores NaN (Se capa por arriba).
        conjunto_x = tabla_de_variable[num_variables_lag:] # tanto en la tabla
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
    patron_a_predecir = tabla_final.tail(1) # Se trata del último patron
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

    print(medias_predichas)

    # return medias_predichas