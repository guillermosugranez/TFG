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
    {'username': 'Guille', 'points': 11},
    {'username': 'Marina', 'points': 9},
    {'username': 'Miguel', 'points': 8},
    {'username': 'Juan', 'points': 10},
    {'username': 'Graci', 'points': 4}
] 


def add_students():
    for student in students:
        try: # Trato de crear todos los registros que haya en la lista
            Student.create(username=student['username'], points=student['points'])

        except IntegrityError: # Si tengo un error de integridad (pe. al tratar de crear un registro con un mismo campo unique repetido...), lanzo este bloque de código.
            students_record = Student.get(username=student['username']) # Recojo un registro usando get. Cojo el que estudiante (registro) deseado (el que tiene el mismo nombre del elemento actual de la lista) 
            students_record.points = student['points'] # Este bloque actualiza el campo points
            students_record.save() # Ahora se guarda la BD. NO OLVIDAR PONER SAVE CADA VEZ QUE SE ACTUALICE UN REGISTRO EN LA BD

def top_student():
    student = Student.select().order_by(Student.points.desc()).get()
    return student

#------------------------------------------------------------------------------------------
# FUNCION PRINCIPAL

if __name__ == '__main__':
    db.connect() # para conectarnos a la base de datos
    db.create_tables([Student], safe=True) # Crea los modelos definidos anteriormente. Safe=True determina que si el modelo ya está creado no ocurra nada si vuelve a intentar crearlo
    #add_students()
    print('El mejor estudiante fue: {}'.format(top_student().username))
    print('El mejor estudiante fue: ' + top_student().username)
