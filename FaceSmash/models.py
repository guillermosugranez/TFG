import datetime
from peewee import *
from flask_login import UserMixin

DATEBASE = SqliteDatabase("social.db")

# Lo más esencial en una red social son los usuarios.
# Hay que definir un modelo que los represente

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=120)
    # Asegurarse de que now es el atributo y no la función
    joined_at = DateTimeField(default=datetime.datetime.now)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    class Meta:
        datebase = DATEBASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        order_by = ("-joined_at")

    # NO HAY QUE REIVENTAR LA RUEDA
    # Para saber si un usuario está ya creado o no, si está logueado o no...
    # Se debe usar otro módulo de la librería de Flask (flask-login)
    # Esto ahorra mucho tiempo y evita posibles errores
    # Para poder usar este módulo hay que ponerle al modelo un mix-in
    # Un mixin es una clase diseñada para agregar funcionalidad a otras clases
    # No tiene sentido usar un mixin por sí misma
    # Se agrega el Mixin deseado desde los parámetros del constructor de clase
    # Partes de este mixin:
    #   - is_authenticated: Es true si el usuario ya inició sesión
    #   - is_active:        True si el usuario ha verificado su eMail
    #   - is_anonymous:     Para usuario anonimos
    #   - get_id():         Regresa un unicode que hace único a cada usuario 
    