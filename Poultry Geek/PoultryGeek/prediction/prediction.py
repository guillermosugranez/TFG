import werkzeug
from flask import Blueprint, url_for, render_template

import pandas as pd

# Predicción
from sklearn.model_selection import train_test_split
from joblib import dump, load
from flask import redirect
from flask import abort

# App
from PoultryGeek import g

# # Dataset ejemplo boston
# from sklearn.datasets import load_boston
# data = load_boston()

# Cargar la base de datos
bp = Blueprint(
    "prediction", __name__, template_folder='templates', static_folder='static')


# ==============================================================================

class evolution_error(werkzeug.exceptions.HTTPException):
    code = 512
    description = 'Error en evolution.'


def obtener_modelo_regresion(
        conjunto_x, conjunto_y, variable, patron_a_predecir):
    # print("Hola Predecir")

    path = 'prediction/modelo_regresion.joblib'
    media_predicha = 0

    # PREDICCIÓN

    # Escalado variables
    from sklearn.preprocessing import StandardScaler
    sc_X = StandardScaler()
    sc_y = StandardScaler()

    patron_a_predecir_scaled = sc_X.fit_transform(patron_a_predecir)
    conjunto_x_scaled = sc_X.fit_transform(conjunto_x)
    conjunto_y_scaled = sc_y.fit_transform(
        conjunto_y[variable].values.reshape(-1, 1))

    try:
        clf = load(path)
    except FileNotFoundError:

        # Lasso CV ----------------
        from sklearn.linear_model import LassoCV
        clf = LassoCV(cv=5, n_jobs=-1)

        clf.fit(conjunto_x_scaled, conjunto_y_scaled.ravel())

        # Se guarda el modelo en bbdd
        dump(clf, path)

    # Desescalado y predicción

    # clf.fit(conjunto_x_scaled, conjunto_y_scaled.ravel())

    try:
        prediccion = clf.predict(patron_a_predecir_scaled)
        media_predicha = sc_y.inverse_transform(prediccion)
    except:
        raise evolution_error

    # print("La media predicha es: ", media_predicha)

    # ENTRENAMIENTO

    # # División training test
    # X_train, X_test, y_train, y_test = (
    # train_test_split(conjunto_x, conjunto_y[variable]))
    # # print(X_test)
    # # print(X_train)
    #
    # # Escalado variables
    # from sklearn.preprocessing import StandardScaler
    # sc_X = StandardScaler()
    # sc_y = StandardScaler()
    # X_train_scaled = sc_X.fit_transform(X_train)
    # y_train_scaled = sc_y.fit_transform(y_train.values.reshape(-1,1))
    # X_test_scaled = sc_X.transform(X_test)
    # y_test_scaled = sc_y.transform(y_test.values.reshape(-1,1))
    # # print(X_test_scaled)
    # # print(y_train_scaled)
    #
    # # SVR ----------------
    # from sklearn.svm import SVR
    # from sklearn.model_selection import GridSearchCV
    # model = SVR()
    # parameters = (
    # [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3],
    #               'C': [1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3],
    #                'epsilon': [1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3]},
    #               {'kernel': ['linear'], 'C': [1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3],
    #                 'epsilon': [1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3]}])
    #
    # # Para comprobar resultado de entrenamiento
    #
    # clf = GridSearchCV(model, parameters, cv=5, n_jobs=-1, scoring='neg_mean_squared_error')
    # clf.fit(X_train_scaled,y_train_scaled.ravel())
    #
    # # Desescalado
    # y_test_predictions = sc_y.inverse_transform(clf.predict(X_test_scaled))
    # from sklearn.metrics import mean_squared_error
    # import math
    # print(
    # 'RMSE SVR %f' % math.sqrt(mean_squared_error(y_test_predictions,y_test)))

    # clf.fit(X_train_scaled, y_train_scaled.ravel())
    #
    # # Desescalado
    # y_test_predictions = sc_y.inverse_transform(clf.predict(X_test_scaled))
    # from sklearn.metrics import mean_squared_error
    # import math
    # print('RMSE SVR %f' % math.sqrt(
    #     mean_squared_error(y_test_predictions, y_test)))

    # # Gradient booting regressor ----------------
    # from sklearn.ensemble import GradientBoostingRegressor
    # model = GradientBoostingRegressor()
    # parameters = {'learning_rate': [0.1, 0.05, 0.01],
    #                       'max_depth': [4, 6, 8],
    #                       'n_estimators': [50, 100, 300]}
    # clf = GridSearchCV(
    # model, parameters, cv=5, n_jobs=-1, scoring='neg_mean_squared_error')
    # clf.fit(X_train_scaled,y_train_scaled.ravel())
    # # Desescalado
    # y_test_predictions = sc_y.inverse_transform(clf.predict(X_test_scaled))
    # print(
    # 'RMSE GBR %f' % math.sqrt(mean_squared_error(y_test_predictions,y_test)))
    #
    #
    # # Lasso CV ----------------
    # from sklearn.linear_model import LassoCV
    # clf = LassoCV(cv=5, n_jobs=-1)
    # # Cv es el número de folds de validación cruzada
    # # n_jobs=-1 indica que se usarán todos los procesadores disponibles
    # clf.fit(X_train_scaled,y_train_scaled.ravel())
    # # Desescalado
    # y_test_predictions = sc_y.inverse_transform(clf.predict(X_test_scaled))
    # print('RMSE LASSO CV %f' % math.sqrt(mean_squared_error(y_test_predictions,y_test)))

    return media_predicha


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

    # print(dict_variable_medias)

    lista_valores_x = []  # Con ellos se forma la tabla final (concat)

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


def predecir(dict_variable_medias):
    """
    Predice la media del mes siguiente para un conjunto de variables

    * Recibe:
        - lista de variables a predecir
        - Diccionario con las medias por meses de cada variable

    * Devuelve:
        - Mismo diccionario con la media del mes siguiente predicha

    """

    # Se obtiene el modelo autoregresivo con las medias calculadas
    valores_y_de_cada_variable, tabla_final, patron_a_predecir = (
        modelo_autoregresivo(
            dict_variable_medias,
            num_variables_lag=3
        )
    )

    # ==========================================================================

    # Se predice el siguiente mes para cada variable
    for variable in dict_variable_medias:
        # Se aplica el modelo que se haya determinado
        media_predicha = obtener_modelo_regresion(
            conjunto_x=tabla_final,
            conjunto_y=valores_y_de_cada_variable,
            variable=variable,
            patron_a_predecir=patron_a_predecir,
        )
        dict_variable_medias[variable].append(media_predicha[0])
        # print(dict_variable_medias[variable])

    return dict_variable_medias

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
