import datetime
from peewee import *

DATEBASE = SqliteDatabase("social.db")

# Lo más esencial en una red social son los usuarios.
# Hay que definir un modelo que los represente

class User(Model):
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