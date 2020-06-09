from peewee import *  # Permite manejar bases datos relacionales usando una base de datos orientada a objetos

db = SqliteDatabase('students.db')

#------------------------------------------------------------------------------------------
# DEFINICION DE MODELOS

class Stduent(Model):
    username = CharField(max_length=255, unique=True)
    points = IntegerField(default=0)

    class Meta:
        database = db

#------------------------------------------------------------------------------------------
# FUNCION PRINCIPAL

if __name__ == '__main__':
    db.connect() # para conectarnos a la base de datos
    db.create_tables([Stduent], safe=True) # Crea los modelos definidos anteriormente. Safe=True determina que si el modelo ya está creado no ocurra nada si vuelve a intentar crearlo