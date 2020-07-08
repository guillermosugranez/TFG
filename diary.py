from peewee import *
import datetime
from collections import OrderedDict # Diccionario ordenado

db = SqliteDatabase('diary.db') # La base de datos de del archivo diary

'''
    Clase Entrada
    - Cada instancia es una entrada del diario
    - Hereda de ka clase Model de peewee
    - Tiene que tener:
        - Una fecha (timestamp)
        - Un contenido

'''
class Entry(Model):

    #   Todos los atributos serán columnas
    #   CharField es para cadenas cortas de texto
    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db

#------------------------------------------------------------------------------------

#   Primero, hacer un esquema básico de la funcionalidad del programa.

'''
Añade una entrada (registro) nueva al diario

'''
def add_entry():
    """Añade una nueva entrada al diario (nuevo registro)"""
    pass

'''
Elimina una entrada (registro) del diario

'''
def delete_entry():
    """Borra una entrada del diario (borra registro)"""
    pass

'''
Despliega todos los registros (entradas)

'''
def view_entries():
    """Muestra todas las entradas del diario (todos los registros)"""
    pass


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
])

'''
Muestra un menú con las opciones
- Es la primera funcionalidad a desarrollar
- No hay switch, se puede hacer con diccionarios, pero para mantener el orden es mejor usar diccionarios ordenados (OrderedDict)
'''
def menu_loop():
    """Muestra el menú con las opciones"""
    choice = None # None es una opción para poner un valor vacío (el usuario no ha elegido de primeras nada)

    while choice != 'q': # Mientras no se elija la opción 'q', se seguirá desplegando el menú
        print("Presiona 'q' para salir")
        for key, value in menu.items():
            print('{}| {}'.format(key, value.__doc__))
        choice = input('Eleccion: ').lower().strip() # lower lo pone todo a minuscula. strip elimina los espacios adicionales

        if choice in menu: # Se desea que las opciones que se envíen esten definidas en el menú (no vale mandar una 'x')
            menu[choice]() # Hace la llamada

'''
Inicializa todo lo relacionado con la bd y crear las tablas

'''
def initialize():
    db.connect() # Primero nos conectamos a la bd
    db.create_tables([Entry], safe = True) # Después nos aseguramos que las tablas existan  
#------------------------------------------------------------------------------------

if __name__ == "__main__":
    initialize()
    menu_loop()

