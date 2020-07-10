from peewee import *
import datetime
from collections import OrderedDict  # Diccionario ordenado

# ------------------------------------------------------------------------------

db = SqliteDatabase('diary.db')  # La base de datos de del archivo diary


class Entry(Model):
    '''Una entrada (Entry) es una entrada en el diario (un registro).

        - Todos los atributos serán columnas
        - CharField es para cadenas cortas de texto
        * Tiene:
            - Una fecha
            - Un contenido
    '''

    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db

# ------------------------------------------------------------------------------

#   Primero, hacer un esquema básico de la funcionalidad del programa.


def add_entry():
    """Añade una nueva entrada al diario (nuevo registro)"""

    pass


def delete_entry():
    """Borra una entrada del diario (borra registro)"""
    pass


def view_entries():
    """Muestra todas las entradas del diario (todos los registros)"""
    pass

# ------------------------------------------------------------------------------

menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
])


def menu_loop():
    """Muestra el menú con las opciones"""

    choice = None  # Inicializa a un valor vacío.

    while choice != 'q':  # Seguirá desplegando el menú mientras no se pulse q
        print("Presiona 'q' para salir")
        for key, value in menu.items():
            print('{}| {}'.format(key, value.__doc__))
        choice = input('Eleccion: ').lower().strip()
        # Por si la entrada no tiene un formato correcto:
        # lower -> Pone todo a minuscula
        # strip -> Elimina los espacios innecesarios

        if choice in menu:  # La opción debe estar definida en el menu
            menu[choice]()


def initialize():
    """Prepara la base de datos"""

    db.connect()  # Se conecta
    db.create_tables([Entry], safe=True)  # Crea las tablas
    # safe=true evita crear modelos ya creados

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    initialize()
    menu_loop()
