from peewee import *  # Permite manejar bases datos relacionales usando una base de datos orientada a objetos

db = SqliteDatabase('students.db')

#------------------------------------------------------------------------------------------
# DEFINICION DE MODELOS

class Student(Model):
    username = CharField(max_length=255, unique=True)
    points = IntegerField(default=0)

    class Meta:
        database = db

# En este array meto los estudiantes. Array de diccionarios
students = [
    {'username': 'Guille', 'points': 10},
    {'username': 'Marina', 'points': 9},
    {'username': 'Miguel', 'points': 8},
    {'username': 'Juan', 'points': 10},
    {'username': 'Graci', 'points': 4}
] 

def add_students():
    for student in students:
        Student.create(username=student['username'], points=student['points'])

#------------------------------------------------------------------------------------------
# FUNCION PRINCIPAL

if __name__ == '__main__':
    db.connect() # para conectarnos a la base de datos
    db.create_tables([Student], safe=True) # Crea los modelos definidos anteriormente. Safe=True determina que si el modelo ya está creado no ocurra nada si vuelve a intentar crearlo
    #add_students()
    Student.create(username='Guille', points=11)
