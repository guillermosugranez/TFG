from peewee import *

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

    Class Meta:
        database = db



#    Primero, hacer un esquema básico de la funcionalidad del programa.


'''
Añade una entrada (registro) nueva al diario

'''
def add_entry():


'''
Elimina una entrada (registro) del diario

'''
def delete_entry():


'''
Despliega todos los registros (entradas)

'''
def delete_entry():


'''
Muestra un menú con las opciones

'''
def menu_loop():

#------------------------------------------------------------------------------------

if if __name__ == "__main__":
    menu_loop()