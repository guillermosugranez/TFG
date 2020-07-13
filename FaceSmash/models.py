import datetime

from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


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
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        datebase = DATEBASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        order_by = ("-joined_at")

    # Constructor
    # cls hace que el método sea de la misma clase, y no de la instancia
    # Esto es aconsejable por legibilidad entre otras cuestiones (PEP8)
    # permite hacer usuario = User.create_user(Guille,guille,guille)...
    # en lugar de:
    #   usuario = User() -> primero se crea la instancia
    #   usuario.create_user(aldo,aldo,aldo) -> luego se vuelve a crear?
    @classmethod
    def create_user(cls, username, email, password):
        try:
            cls.create( # Crea un registro en la bbdd
                username=username,
                email=email,
                password=generate_password_hash(password),
            )
        except IntegrityError:
            raise ValueError("User Already exists")

# -----------------------------------------------------------------------------
# Lección 34. UserMixin

# NO HAY QUE REIVENTAR LA RUEDA
# Para saber si un usuario está ya creado o no, si está logueado o no...
# Se debe usar otro módulo de la librería de Flask (flask-login)
# Esto ahorra mucho tiempo y evita posibles errores
# Para poder usar este módulo hay que ponerle al modelo un mix-in
# Un mixin es una clase diseñada para agregar funcionalidad a otras clases
# No tiene sentido usar un mixin por sí misma
# Se agrega el Mixin deseado desde los parámetros de la definición de clase
# Partes de este mixin:
#   - is_authenticated: Es true si el usuario ya inició sesión
#   - is_active:        True si el usuario ha verificado su eMail
#   - is_anonymous:     Para usuario anonimos
#   - get_id():         Regresa un unicode que hace único a cada usuario

# -----------------------------------------------------------------------------
# Lección 35. Encriptación y Hasing

# No guardar las password como texto plano.
# Se usarán algoritmos de hasing. La encriptación es obsoleta en este caso.
# Cuando se le pasa la función Hash a un texto, no hay manera de volver atrás
# Para poder usar esta funcionalidad en la aplicación se usa flask_bcrypt

# Al generar un password desde una cadena, el resultado es diferente cada vez:
#   >>> from flask_bcrypt import generate_password_hash
#   >>> generate_password_hash('aldo')
#   b'$2b$12$ke06Vq2J315W6fZX69mDxObFsOyfYrx5IX77DNhdjJVWsVj2HLTEC'
#   >>> generate_password_hash('aldo')
#   b'$2b$12$umfZGyJacQtTZDES0jh.c.dZcj5Y9FcsdhM8lgI5BmpqJBlgiTkRq'
#   >>>
# Para poder volver atrás:
#   >>> password_aldo = generate_password_hash('aldo')
#   >>> from flask_bcrypt import check_password_hash
#   >>> check_password_hash(password_aldo, 'aldo')
#   True
#   >>>

# -----------------------------------------------------------------------------
