from peewee import *
import datetime

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
    pass

'''
Elimina una entrada (registro) del diario

'''
def delete_entry():
    pass

'''
Despliega todos los registros (entradas)

'''
def view_entries():
    pass

'''
Muestra un menú con las opciones

'''
def menu_loop():
    pass

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

