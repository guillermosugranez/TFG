from peewee import *
import datetime
import sys  # sys.stdin.read().strip()                              
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
    # La hora se establece en el consturctor de clase
    timestamp = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db

# ------------------------------------------------------------------------------

#   Primero, hacer un esquema básico de la funcionalidad del programa.


def add_entry():
    """Añade una nueva entrada al diario (nuevo registro)"""

    # Mostrar instrucciones
    print("Introduce tu registro. Presiona Ctrl+Z+Enter cuando termines.")
    # data Contiene el texto que va introducir el usuario
    # Se usa sys.stdin.read() para poder usar Ctrl+z+Enter como final de texto.
    # En otros SOs, buscar EOF correspondiente
    data = sys.stdin.read().strip()

    if data:
        if input("Guardar entrada? [Yn]").lower() != 'n':
            Entry.create(content=data)
            print('Guardar exitosamente')

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
