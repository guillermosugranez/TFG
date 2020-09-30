import pandas as pd
import os.path

def make_dataset(folder_name):
    """
    Dado el nombre de una carpeta, genera un dataset con todos los ficheros
    excel que encuentre.

    Nota: La carpeta debe estar alojada en la misma carpeta que el script
    """

    path = os.getcwd() + "/" + folder_name  # Carpeta donde se ejecuta el script
    files = os.listdir(path)  # Archivos en la carpeta
    dataframes = []  # Lista vacía de dataframes

    for file in files:
        filename, extension = os.path.splitext(str(file))
        if extension == ".xlsx":  # Solo archivos excel
            data = pd.read_excel(path + "/" + file)
            dataframes.append(data)  # Nuevo dataframe generado
            # print(data.head())

        else:
            print("Archivo descartado: ", file)

    # pd.concat(data,

    return pd.concat(dataframes)

if __name__ == "__main__":
    """Making Dataset"""

    dataset = make_dataset("Tables")  # Se le pasa el nombre de la carpeta
    print(dataset)