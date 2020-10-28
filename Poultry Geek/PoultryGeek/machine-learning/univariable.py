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
    nombre_variable = 'pollos_salidos'
    m = [9, 8, 7, 7, 7, 5, 3, 5, 5, 6, 7, 4, 5, 7, 5, 4, 3, 5, 6, 7, 8, 5]
    dataframe_medias = pd.DataFrame(m)

    # Se crea la primera columna de la tabla
    tabla = pd.DataFrame(m, columns=[nombre_variable])

    # Se forman las variables con lag y con ellas se completa la tabla
    for i in range(num_variables_lag):
        # indice = 'C' + str(i)
        dataframe_medias = dataframe_medias.shift(periods=1)
        tabla.insert(i+1,("t-" + str(i+1)), dataframe_medias)

    # Se forma el conjunto de resultados (columna y)
    y = pd.DataFrame(m, columns=["y"])
    y = y.shift(periods=-1) # Se desplaza una posición hacia arriba

    # print("La tabla original\n", tabla, y)

    # Se quitan las filas con valores NaN (en función del nº de variables lag)
    conjunto_x = tabla[num_variables_lag:] # tanto en la tabla
    conjunto_y = y[num_variables_lag:]  # como en la columna de resultados

    # print("La tabla capada por arriba\n", conjunto_x, conjunto_y)

    # Se saca la variable a predecir:
    patron_a_predecir = conjunto_x.tail(1) # Se trata del último patron

    # Coge todas las filas menos la última
    conjunto_x = conjunto_x.iloc[:-1]
    conjunto_y = conjunto_y.iloc[:-1]

    print("patron a predecir" + str(patron_a_predecir.shape) + ". \n", patron_a_predecir)
    print("\nLas x" + str(conjunto_x.shape) + ". \n", conjunto_x)
    print("\nLas y" + str(conjunto_y.shape) + ". \n", conjunto_y)

    # ==========================================================================
    # Determinar la bondad del modelo

    # Split the data into training/testing sets
    # X_train, X_test, y_train, y_test = train_test_split(
    #     conjunto_x, conjunto_y, test_size=0.15, random_state=42
    # )
    #
    # print("\nX_train" + str(X_train.shape) + "\n", X_train)
    # print("\ny_train" + str(y_train.shape) + "\n", y_train)
    #
    # print("\nX_test" + str(X_test.shape) + "\n", X_test)
    # print("\ny_test" + str(y_test.shape) + "\n", y_test)

    # Split the targets into training/testing sets
    # diabetes_y_train = diabetes_y[:-20]
    # diabetes_y_test = diabetes_y[-20:]

    # y = pd.DataFrame(m, columns=["y"])
    # y = y.shift(periods=-1)
    # print(y)

    # # Create linear regression object
    # regr = linear_model.LinearRegression()
    #
    # # Train the model using the training sets
    # regr.fit(X_train, y_train)
    #
    # # Make predictions using the testing set
    # y_pred = regr.predict(X_test)
    #
    # print("\ny_pred" + str(y_pred.shape) + "\n", y_pred)

    # # The coefficients
    # print('Coefficients: \n', regr.coef_)
    # # The mean squared error
    # print('Mean squared error: %.2f'
    #       % mean_squared_error(y_test, y_pred))
    # # The coefficient of determination: 1 is perfect prediction
    # print('Coefficient of determination: %.2f'
    #       % r2_score(y_test, y_pred))

    # ==========================================================================
    # Usar todos los datos disponibles para predecir
    # Se aplica el modelo que se haya determinado

    regr = linear_model.LinearRegression()
    regr.fit(conjunto_x, conjunto_y)
    y_pred = regr.predict(patron_a_predecir)

    print("El patron predicho es: ", y_pred)

    # ==========================================================================

    # Plot outputs
    # plt.scatter(X_test, y_test,  color='black')
    # plt.plot(X_test, y_pred, color='blue', linewidth=3)
    #
    # plt.xticks(())
    # plt.yticks(())

    plt.show()